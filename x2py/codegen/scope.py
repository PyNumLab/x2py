"""Module containing the Scope class"""

from immutabledict import immutabledict

from .bind_c import BindCVariable
from .models.datatypes import TupleType
from .models.core import ClassDef
from .models.core import Symbol
from .models.core import (
    DottedVariable,
    IndexedElement,
    Variable,
)
from x2py.naming import NamingPolicy
from x2py.naming import generated_symbol_rules
from x2py.utilities.strings import create_incremented_string


def _resolve_scope_naming_state(parent_scope, naming_policy, public_namespace, symbol_language):
    """Return inherited naming policy, public namespace, and symbol language."""
    if naming_policy is None and parent_scope is not None:
        naming_policy = parent_scope.naming_policy
    if naming_policy is None:
        naming_policy = NamingPolicy()
    if public_namespace is None and parent_scope is not None:
        public_namespace = parent_scope.public_namespace
    if symbol_language is None and parent_scope is not None:
        symbol_language = parent_scope.symbol_language
    if symbol_language is None:
        symbol_language = "python"
    generated_symbol_rules(symbol_language)
    return naming_policy, tuple(public_namespace or ()), symbol_language.casefold()


class Scope:
    """
    Class representing all objects defined within a given scope.

    This class provides all necessary functionalities for creating new object
    names without causing name clashes. It also stores all objects defined
    within the scope. This allows us to search for variables only in relevant
    scopes.

    Parameters
    ----------
    name : str, optional
        The name of the scope. The value needs to be provided when it is not a loop.

    decorators : dict, default: ()
        A dictionary of any decorators which operate on objects in this scope.

    is_loop : bool, default: False
        Indicates if the scope represents a loop (in Python variables declared
        in loops are not scoped to the loop).

    parent_scope : Scope, default: None
        The enclosing scope.

    used_symbols : dict, default: None
        A dictionary mapping all the names which we know will appear in the scope and which
        we therefore want to avoid when creating new names to their collisionless name.

    original_symbols : dict, default: None
        A dictionary which maps names used in the code to the original name used
        in the Python code.

    symbolic_aliases : dict, optional
        A dictionary which maps indexed tuple elements to variables representing those
        elements. This argument should only be used after the semantic stage.

    naming_policy : NamingPolicy, optional
        Shared policy used for public Python names and generated target-language
        symbols. Child scopes inherit this from their parent.

    public_namespace : tuple[str, ...], optional
        Namespace key used when reserving public Python names.

    symbol_language : str, optional
        Target language used when reserving generated symbols.

    scope_type : str
        The type of the scope being created [module, function, class, loop, program].
    """

    allow_loop_scoping = False
    __slots__ = (
        "_dotted_symbols",
        "_dummy_counter",
        "_imports",
        "_is_loop",
        "_locals",
        "_loops",
        "_name",
        "_naming_policy",
        "_original_symbol",
        "_parent_scope",
        "_public_namespace",
        "_scope_type",
        "_sons_scopes",
        "_symbol_language",
        "_symbol_prefix",
        "_temporary_variables",
        "_used_symbols",
    )

    categories = (
        "functions",
        "variables",
        "classes",
        "imports",
        "symbolic_aliases",
        "decorators",
        "cls_constructs",
    )

    def __init__(
        self,
        *,
        name=None,
        decorators=(),
        is_loop=False,
        parent_scope=None,
        used_symbols=None,
        original_symbols=None,
        naming_policy=None,
        public_namespace=None,
        symbol_language=None,
        symbolic_aliases=None,
        scope_type,
    ):
        assert (name is None) != (not is_loop)
        assert scope_type in ("module", "function", "class", "loop", "program")

        self._name = name
        self._scope_type = scope_type
        self._imports = {k: {} for k in self.categories}

        self._locals = {k: {} for k in self.categories}

        prefix_set = ()
        if parent_scope and parent_scope.symbol_prefix:
            prefix_set += (parent_scope.symbol_prefix.removesuffix("__"),)
        if name:
            prefix_set += (name,)

        self._symbol_prefix = "__".join((*prefix_set, ""))

        self._temporary_variables = []

        if used_symbols and not isinstance(used_symbols, dict):
            raise RuntimeError("Used symbols must be a dictionary")

        self._used_symbols = used_symbols or {}
        self._original_symbol = original_symbols or {}
        self._naming_policy, self._public_namespace, self._symbol_language = _resolve_scope_naming_state(
            parent_scope,
            naming_policy,
            public_namespace,
            symbol_language,
        )

        self._dummy_counter = 0

        self._locals["decorators"].update(decorators)
        if symbolic_aliases:
            self._locals["symbolic_aliases"].update(symbolic_aliases)

        # TODO use another name for headers
        #      => reserved keyword, or use __
        self._parent_scope = parent_scope
        self._sons_scopes = {}

        self._is_loop = is_loop
        # scoping for loops
        self._loops = []

        self._dotted_symbols = []

    def new_child_scope(self, name, scope_type, **kwargs):
        """
        Create a new child Scope object which has the current object as parent.

        The parent scope can access the child scope through the '_sons_scopes'
        dictionary, using the provided name as key. Conversely, the child scope
        can access the parent scope through the 'parent_scope' attribute.

        Parameters
        ----------
        name : str
            Name of the new scope, used as a key to retrieve the new scope.
        scope_type : str
            The type of the scope being created [module, function, class, loop, program].
        **kwargs : dict
            Keyword arguments passed to __init__() for object initialization.

        Returns
        -------
        Scope
            New child scope, which has the current object as parent.
        """
        ps = kwargs.pop("parent_scope", self)
        if ps is not self:
            raise ValueError(f"A child of {self} cannot have a parent {ps}")

        child = Scope(name=name, **kwargs, parent_scope=self, scope_type=scope_type)

        self.add_son(name, child)

        return child

    @property
    def naming_policy(self):
        """Policy used to reserve public names and generated symbols."""
        return self._naming_policy

    @property
    def public_namespace(self):
        """Namespace key used for public wrapper name reservations."""
        return self._public_namespace

    @property
    def symbol_language(self):
        """Target language used for generated-symbol reservations."""
        return self._symbol_language

    def child_public_namespace(self, *parts):
        """Return a child public namespace below the current scope."""
        return (*self._public_namespace, *(str(part) for part in parts))

    @property
    def name(self):
        """
        The name of the scope.

        The name of the scope.
        """
        return self._name

    @property
    def symbol_prefix(self):
        """
        The prefix used for symbols.

        The prefix that may be prepended to symbols for context information.
        """
        return self._symbol_prefix

    @property
    def imports(self):
        """A dictionary of objects imported in this scope"""
        return self._imports

    @property
    def variables(self):
        """
        A dictionary of variables defined in this scope.

        A dictionary whose keys are the original Python names of the variables
        in the scope and whose values are Variable objects. When handling an
        inlined function it is possible that some of the values will not be
        Variable objects but rather the value that the variable takes in this
        context.
        """
        return immutabledict(self._locals["variables"])

    @property
    def classes(self):
        """
        A dictionary of classes defined in this scope.

        A dictionary whose keys are the original Python names of the classes
        in the scope and whose variables are ClassDef objects.
        """
        return immutabledict(self._locals["classes"])

    @property
    def functions(self):
        """
        A dictionary of functions defined in this scope.

        A dictionary whose keys are the original Python names of the functions
        in the scope and whose variables are ClassDef objects.
        """
        return immutabledict(self._locals["functions"])

    @property
    def decorators(self):
        """
        A dictionary of the decorators applied to the current function.

        A dictionary of the decorators which are applied to the function definition
        in this scope. The keys are the name of the decorator function. The values
        depend on the decorator.
        """
        return immutabledict(self._locals["decorators"])

    @property
    def cls_constructs(self):
        """
        A dictionary of datatypes for the classes defined in this scope.

        A dictionary whose keys are the original Python names of the classes
        found in this scope and whose values are the types inheriting from
        Type which identify these classes.
        """
        return immutabledict(self._locals["cls_constructs"])

    @property
    def symbolic_aliases(self):
        """
        A dictionary of symbolic alias defined in this scope.

        A symbolic alias is a symbol declared in the scope which is mapped
        to a constant object. E.g. a symbol which represents a type.
        """
        return immutabledict(self._locals["symbolic_aliases"])

    def find(self, name, category=None, local_only=False, raise_if_missing=False):
        """
        Find and return the specified object in the scope.

        Find a specified object in the scope and return it.
        The object is identified by a string containing its name.
        If the object cannot be found then None is returned unless
        an error is requested.

        Parameters
        ----------
        name : str
            The Python name of the object we are searching for.
        category : str, optional
            The type of object we are searching for.
            This must be one of the strings in Scope.categories.
            If no value is provided then we look in all categories.
        local_only : bool, default=False
            Indicates whether we should look for variables in the
            entire scope or whether we should limit ourselves to the
            local scope.
        raise_if_missing : bool, default=False
            Indicates whether an error should be raised if the object
            cannot be found.

        Returns
        -------
        codegen model object
            The object stored in the scope.
        """
        for local_category in [category] if category else self._locals.keys():
            if name in self._locals[local_category]:
                return self._locals[local_category][name]

            if name in self.imports[local_category]:
                return self.imports[local_category][name]

        # Walk up the tree of Scope objects, until the root if needed
        if self.parent_scope and (self.is_loop or not local_only):
            return self.parent_scope.find(name, category, local_only, raise_if_missing)
        if raise_if_missing:
            raise RuntimeError(f"Can't find expected object {name} in scope")
        return None

    def find_all(self, category):
        """
        Find and return all objects from the specified category in the scope.

        Find and return all objects from the specified category in the scope.

        Parameters
        ----------
        category : str
            The type of object we are searching for.
            This must be one of the strings in Scope.categories.

        Returns
        -------
        dict
            A dictionary containing all the objects of the specified category
            found in the scope.
        """
        result = self.parent_scope.find_all(category) if self.parent_scope else {}

        result.update(self._locals[category])
        result.update(self._imports[category])

        return result

    @property
    def is_loop(self):
        """Indicates whether this scope describes a loop"""
        return self._is_loop

    def create_new_loop_scope(self):
        """
        Create a new Scope within the current scope describing a loop.

        Create a new Scope within the current scope describing a loop
        (For/While/etc).

        Returns
        -------
        Scope
            The newly created loop scope.
        """
        new_scope = Scope(
            decorators=self.decorators,
            is_loop=True,
            parent_scope=self,
            scope_type="loop",
        )
        self.add_loop(new_scope)
        return new_scope

    def insert_variable(self, var, name=None):
        """
        Add a variable to the current scope.

        Add a variable to the current scope.

        Parameters
        ----------
        var : Variable
            The variable to be inserted into the current scope.
        name : str, default=var.name
            The name of the variable in the Python code.
        """
        if var.name == "_":
            raise ValueError("A temporary variable should have a name generated by Scope.get_new_name")
        if not isinstance(var, Variable):
            raise TypeError("variable must be of type Variable")

        if name is None:
            name = self.get_python_name(var.name)

        if not self.allow_loop_scoping and self.is_loop:
            self.parent_scope.insert_variable(var, name)
        else:
            if name in self._locals["variables"]:
                if name in self.symbolic_aliases.values():
                    # If the syntactic name is in the symbolic aliases then the link was created
                    # at the syntactic stage. In this case the element will be created before the
                    # tuple
                    return
                raise RuntimeError(f"New variable {name} already exists in scope")

            if name == "_":
                self._temporary_variables.append(var)
            else:
                self._locals["variables"][name] = var

    def remove_variable(self, var, name=None, remove_symbol=True):
        """
        Remove a variable from anywhere in scope.

        Remove a variable from anywhere in scope.

        Parameters
        ----------
        var : Variable
                The variable to be removed.
        name : str, optional
                The name of the variable in the python code
                Default : var.name.
        remove_symbol : bool, default=True
                Indicate if the associated symbol should also be removed. This is assumed
                to be true but it may need to be set to false if the variable is removed
                in order to update the definition.
        """
        if name is None:
            name = self.get_python_name(var.name)

        if name in self._locals["variables"]:
            self._locals["variables"].pop(name)
            if remove_symbol:
                self._used_symbols.pop(name)
        elif self.parent_scope:
            self.parent_scope.remove_variable(var, name)
        else:
            raise RuntimeError("Variable not found in scope")

    def insert_class(self, cls, name=None):
        """
        Add a class to the current scope.

        Add the definition of a class to the current scope to
        make it discoverable when used.

        Parameters
        ----------
        cls : ClassDef
            The class to be inserted into the current scope.

        name : str, optional
            The name under which the classes should be indexed in the scope.
            This defaults to the name of the class in Python.
        """
        if not isinstance(cls, ClassDef):
            raise TypeError("class must be of type ClassDef")

        assert not self.is_loop

        if name is None:
            name = cls.name
            name = self.get_python_name(name)
        if name in self._locals["classes"]:
            raise RuntimeError(f"A class with name '{name}' already exists in the scope")
        assert name in self._used_symbols
        self._locals["classes"][name] = cls

    def insert_cls_construct(self, class_type):
        """
        Add a class construct to the scope.

        Add a class construct to the scope. A class construct is a type inheriting from
        Type which describes the type of a class.

        Parameters
        ----------
        class_type : Type
            The construct to be inserted.
        """
        name = class_type.name
        self._locals["cls_constructs"][name] = class_type

    def insert_function(self, func, name):
        """
        Add a function to the scope.

        Add a function to the scope. The key will be the original name of the
        function in the Python code.

        Parameters
        ----------
        func : FunctionDef
            The function to be inserted.
        name : str | Symbol
            The original name of the function in the Python code. This will be
            used as the key for the function in the scope.
        """
        assert name in self._used_symbols
        assert name not in self._locals["functions"]
        self._locals["functions"][name] = func

    def insert_symbol(self, symbol, object_type="variable"):
        """
        Add a new symbol to the scope.

        Add a new symbol to the scope in the syntactic stage. This should be used to
        declare symbols defined by the user. Once the symbol is declared the Scope
        generates a collisionless name if necessary which can be used in the target
        language without causing problems by being a keyword or being confused with
        other symbols (e.g. in Fortran which is not case-sensitive). This new name
        can be retrieved later using `Scope.get_expected_name`.

        Parameters
        ----------
        symbol : Symbol | DottedName
            The symbol to be added to the scope.

        object_type : str, default=variable
            The type of the object for which a name is requested (e.g. module, function,
            class, variable).

        Returns
        -------
        Symbol | DottedName
            The new collisionless symbol that will be used in the low-level code.
        """

        if type(symbol).__name__ == "AnnotatedSymbol":
            symbol = symbol.name

        if not self.allow_loop_scoping and self.is_loop:
            return self.parent_scope.insert_symbol(symbol)
        if symbol not in self._used_symbols:
            collisionless_name = self._naming_policy.generated_symbol(
                symbol,
                self.all_used_symbols,
                language=self._symbol_language,
                prefix=self._symbol_prefix,
                context=object_type,
                parent_context=self._scope_type,
            )
            collisionless_symbol = Symbol(collisionless_name, is_temp=getattr(symbol, "is_temp", False))
            self._used_symbols[symbol] = collisionless_symbol
            self._original_symbol[collisionless_symbol] = symbol
            return collisionless_symbol
        return self._used_symbols[symbol]

    def insert_low_level_symbol(self, python_symbol, low_level_symbol):
        """
        Add a new symbol to the scope for which the low-level equivalent is known.

        Add a new symbol to the scope in the syntactic stage. This should be used to
        declare symbols defined by the user but mapped to a low-level name (e.g. via
        @low_level).

        Parameters
        ----------
        python_symbol : Symbol
            The symbol to be added to the scope.
        low_level_symbol : Symbol
            The low-level equivalent of the symbol being added to the scope.
        """

        if not self.allow_loop_scoping and self.is_loop:
            self.parent_scope.insert_low_level_symbol(python_symbol, low_level_symbol)

        assert python_symbol not in self._used_symbols

        if self._naming_policy.has_generated_symbol_clash(
            low_level_symbol,
            self.all_used_symbols,
            language=self._symbol_language,
        ):
            raise ValueError("Low-level name conflicts with name already in use.")

        self._used_symbols[python_symbol] = low_level_symbol
        self._original_symbol[low_level_symbol] = python_symbol

    def remove_symbol(self, symbol):
        """
        Remove symbol from the scope.

        Remove symbol from the scope.

        Parameters
        ----------
        symbol : Symbol
            The symbol to be removed from the scope.
        """

        if symbol in self._used_symbols:
            collisionless_symbol = self._used_symbols.pop(symbol)
            self._original_symbol.pop(collisionless_symbol)

    def insert_symbolic_alias(self, symbol, alias):
        """
        Add a new symbolic alias to the scope.

        A symbolic alias is a symbol declared in the scope which is mapped
        to a constant object. E.g. a symbol which represents a type.

        Parameters
        ----------
        symbol : Symbol
            The symbol which will represent the object in the code.
        alias : object
            The object which will be represented by the symbol.
        """
        if not self.allow_loop_scoping and self.is_loop:
            self.parent_scope.insert_symbolic_alias(symbol, alias)
        else:
            symbolic_aliases = self._locals["symbolic_aliases"]
            if symbol in symbolic_aliases:
                raise ValueError(f"{symbol} cannot represent multiple static concepts")

            symbolic_aliases[symbol] = alias

    @property
    def all_used_symbols(self):
        """
        Get all low-level symbols which already exist in this scope.

        Get a set containing all low-level symbols which already exist
        in this scope.
        """
        symbols = self.parent_scope.all_used_symbols if self.parent_scope else set()
        symbols.update(self._used_symbols.values())
        return symbols

    @property
    def all_python_symbols(self):
        """
        Get all Python symbols which already exist in this scope.

        Get a set containing all Python symbols which already exist
        in this scope.
        """
        symbols = self.parent_scope.all_python_symbols if self.parent_scope else set()
        symbols.update(self._used_symbols.keys())
        return symbols

    @property
    def local_used_symbols(self):
        """
        Get all symbols which already exist in this local scope.

        Get the dictionary describing all symbols which already exist
        in the local scope. The local scope is this scope excluding
        enclosing scopes. The dictionary's keys are existing symbols
        (that were used in the original Python code). Its values are
        the collisionless symbols that will be used in the low-level
        code to describe these objects.
        """
        return self._used_symbols

    def symbol_in_use(self, name):
        """
        Determine if a name is already in use in this scope.

        Determine if a name is already in use in this scope.

        Parameters
        ----------
        name : Symbol
            The name we are searching for.

        Returns
        -------
        bool
            True if the name has already been inserted into this scope, False otherwise.
        """
        if name in self._used_symbols:
            return True
        if self.parent_scope:
            return self.parent_scope.symbol_in_use(name)
        return False

    def get_new_name(self, current_name=None, *, is_temp=None, object_type="variable"):
        """
        Get a new name which does not clash with any names in the current context.

        Creates a new name. A current_name can be provided indicating the name the
        user would like to use if possible. If this name is not available then it
        will be used as a prefix for the new name.
        If no current_name is provided, then the standard prefix is used, and the
        dummy counter is used and updated to facilitate finding the next value of
        this common case.

        Parameters
        ----------
        current_name : str, default: None
            The name the user would like to use if possible.

        is_temp : bool, optional
            Indicates if the generated symbol should be a temporary (i.e. an extra
            temporary object generated by X2py). This is always the case if no
            current_name is provided.

        object_type : str, default=variable
            The type of the object for which a name is requested (e.g. module, function,
            class, variable).

        Returns
        -------
        Symbol
            The new name which will be printed in the code.
        """
        if current_name is not None and not self._naming_policy.has_generated_symbol_clash(
            current_name,
            self.all_python_symbols,
            language=self._symbol_language,
        ):
            new_name = Symbol(current_name, is_temp=is_temp)
            return self.insert_symbol(new_name, object_type=object_type)

        if current_name is None:
            assert is_temp is None
            is_temp = True
            # Avoid confusing names by also searching in parent scopes
            new_name, self._dummy_counter = create_incremented_string(
                self.all_used_symbols,
                prefix=current_name,
                counter=self._dummy_counter,
                naming_rules=generated_symbol_rules(self._symbol_language),
            )
        else:
            if is_temp is None:
                is_temp = True
            # When a name is suggested, try to stick to it
            new_name, _ = create_incremented_string(self.all_used_symbols, prefix=current_name)

        collisionless_name = self._naming_policy.generated_symbol(
            new_name,
            self.all_used_symbols,
            language=self._symbol_language,
            prefix=self._symbol_prefix,
            context=object_type,
            parent_context=self._scope_type,
        )
        collisionless_symbol = Symbol(collisionless_name, is_temp=True)
        self._used_symbols[collisionless_symbol] = collisionless_symbol
        self._original_symbol[collisionless_symbol] = collisionless_symbol
        return self.insert_symbol(collisionless_symbol, object_type)

    def reserve_public_name(self, raw_name, *, object_type="variable", owner=None):
        """Reserve a Python-visible name in this scope's public namespace."""
        return self._naming_policy.reserve_public_name(
            self._public_namespace,
            raw_name,
            category=object_type,
            owner=owner,
        )

    def get_new_public_name(
        self,
        current_name=None,
        *,
        python_name=None,
        is_temp=None,
        object_type="variable",
        owner=None,
    ):
        """Create a low-level symbol and map it to a reserved Python public name."""
        raw_public_name = current_name if python_name is None else python_name
        public_name = self.reserve_public_name(raw_public_name, object_type=object_type, owner=owner)
        symbol_object_type = "variable" if object_type in {"argument", "field"} else object_type
        symbol = self.get_new_name(
            current_name if current_name is not None else public_name,
            is_temp=is_temp,
            object_type=symbol_object_type,
        )
        self._original_symbol[symbol] = public_name
        return symbol

    def get_temporary_variable(self, dtype_or_var, name=None, **kwargs):
        """
        Get a temporary variable.

        Get a temporary variable.

        Parameters
        ----------
        dtype_or_var : str, DataType, Variable
            In the case of a string of DataType: The type of the Variable to be created
            In the case of a Variable: a Variable which will be cloned to set all the Variable properties.
        name : str, optional
            The requested name for the new variable.
        **kwargs : dict
            See Variable keyword arguments.

        Returns
        -------
        Variable
            The temporary variable.
        """
        assert isinstance(name, str | type(None))
        name = self.get_new_name(name)
        if isinstance(dtype_or_var, Variable):
            var = dtype_or_var.clone(name, **kwargs, is_temp=True)
        else:
            var = Variable(dtype_or_var, name, **kwargs, is_temp=True)

        self.insert_variable(var)
        return var

    def get_expected_name(self, start_name):
        """
        Get a name with no collisions.

        Get a name with no collisions, ideally the provided name.
        The provided name should already exist in the symbols.

        Parameters
        ----------
        start_name : str
            The name which was used in the Python code.

        Returns
        -------
        Symbol
            The name which will be used in the generated code.
        """
        if start_name == "_":
            return self.get_new_name()
        if start_name in self._used_symbols:
            return self._used_symbols[start_name]
        if self.parent_scope:
            return self.parent_scope.get_expected_name(start_name)
        raise RuntimeError(f"{start_name} does not exist in scope")

    def get_import_alias(self, obj, category=None):
        """
        Get the name used to access an imported object in the current scope.

        Get the name used to access an imported object in the current scope.
        This is different to the current name when the function was imported
        with import X as Y, but only some languages are capable of renaming
        methods in this way so the original object's name shouldn't be
        modified.

        Parameters
        ----------
        obj : model object
            The object we are searching for.
        category : str, optional
            The type of object we are searching for.
            This must be one of the strings in Scope.categories.
            If no value is provided then we look in all categories.

        Returns
        -------
        str
            The name used to access an imported object in the current scope.
        """
        for local_category in [category] if category else self._locals.keys():
            import_obj = self.imports[local_category]
            name = next((n for n, o in import_obj.items() if o is obj), None)
            if name:
                return name

        if self.parent_scope:
            return self.parent_scope.get_import_alias(obj, category)
        raise RuntimeError(f"Can't find expected imported object {obj} in scope")

    def collect_all_imports(self):
        """Collect the names of all modules necessary to understand this scope"""
        imports = list(self._imports["imports"].keys())
        imports.extend([i for s in self._sons_scopes.values() for i in s.collect_all_imports()])
        return imports

    def collect_all_type_vars(self):
        """
        Collect all TypeVar objects which are available in this scope.

        Collect all TypeVar objects which are available in this scope. This includes
        TypeVars declared in parent scopes.

        Returns
        -------
        list[TypeVar]
            A list of TypeVars in the scope.
        """
        type_vars = {n: t for n, t in self.symbolic_aliases.items() if type(t).__name__ == "TypingTypeVar"}
        if self.parent_scope:
            parent_type_vars = self.parent_scope.collect_all_type_vars()
            parent_type_vars.update(type_vars)
            return parent_type_vars
        return type_vars

    def update_parent_scope(self, new_parent, is_loop, name=None):
        """Change the parent scope"""
        if is_loop:
            if self.parent_scope:
                self.parent_scope.remove_loop(self)
            self._parent_scope = new_parent
            self.parent_scope.add_loop(self)
        else:
            if self.parent_scope:
                name = self.parent_scope.remove_son(self)
            self._parent_scope = new_parent
            self.parent_scope.add_son(name, self)

    @property
    def parent_scope(self):
        """Return the enclosing scope"""
        return self._parent_scope

    def remove_loop(self, loop):
        """Remove a loop from the scope"""
        self._loops.remove(loop)

    def remove_son(self, son):
        """Remove a sub-scope from the scope"""
        name = [k for k, v in self._sons_scopes.items() if v is son]
        assert len(name) == 1
        self._sons_scopes.pop(name[0])

    def add_loop(self, loop):
        """Make parent aware of new child loop"""
        assert loop.parent_scope is self
        self._loops.append(loop)

    def add_son(self, name, son):
        """Make parent aware of new child"""
        assert son.parent_scope is self
        self._sons_scopes[name] = son

    def get_python_name(self, name):
        """
        Get the name used in the original Python code.

        Get the name used in the original Python code from the name used
        by the variable that was created in the parser.

        Parameters
        ----------
        name : Symbol | str
            The name of the Variable in the generated code.

        Returns
        -------
        str
            The name of the Variable in the original code.
        """
        if name in self._original_symbol:
            return self._original_symbol[name]
        if self.parent_scope:
            return self.parent_scope.get_python_name(name)
        raise RuntimeError(f"Can't find {name} in scope")

    @property
    def python_names(self):
        """Get map of new names to original python names"""
        return self._original_symbol

    def collect_tuple_element(self, tuple_elem):
        """
        Get an element of a tuple.

        This function is mainly designed to handle inhomogeneous tuples. Such tuples
        cannot be directly represented in low-level languages. Instead they are replaced
        by multiple variables representing each of the elements of the tuple. This
        function maps tuple elements (e.g. `var[0]`) to the variable representing that
        element in the low-level language (e.g. `var_0`).

        Parameters
        ----------
        tuple_elem : model object
            The element of the tuple obtained via the `__getitem__` function.

        Returns
        -------
        Variable
            The variable which represents the tuple element in a low-level language.

        Raises
        ------
        X2pyError
            An error is raised if the tuple element has not yet been added to the scope.
        """
        if isinstance(tuple_elem, IndexedElement) and isinstance(tuple_elem.base, DottedVariable):
            cls_scope = tuple_elem.base.lhs.cls_base.scope
            if cls_scope is not self:
                return cls_scope.collect_tuple_element(tuple_elem)

        if isinstance(tuple_elem, IndexedElement) and isinstance(tuple_elem.base.class_type, TupleType):
            for element, alias in self.symbolic_aliases.items():
                if (
                    isinstance(element, IndexedElement)
                    and element.base is tuple_elem.base
                    and element.indices == tuple_elem.indices
                ):
                    return alias
            raise RuntimeError(f"Tuple element {tuple_elem} has no symbolic alias")

        return tuple_elem

    def collect_all_tuple_elements(self, tuple_var):
        """
        Create a tuple of variables from a variable representing an inhomogeneous object.

        Create a tuple of variables that can be printed in a low-level language. An
        inhomogeneous object cannot be represented as is in a low-level language so
        it must be unpacked into a PythonTuple. This function is recursive so that
        variables with a type such as `tuple[tuple[int,bool],float]` generate
        `PythonTuple(PythonTuple(var_0_0, var_0_1), var_1)`.

        Parameters
        ----------
        tuple_var : Variable | FunctionAddress
            A variable which may or may not be an inhomogeneous tuple.

        Returns
        -------
        list[Variable]
            All variables that should be printed in a low-level language to represent
            the Variable.
        """
        if isinstance(tuple_var, BindCVariable):
            tuple_var = tuple_var.new_var

        if isinstance(tuple_var, Variable) and isinstance(tuple_var.class_type, TupleType):
            elements = []
            for i in range(len(tuple_var.class_type)):
                element = self.collect_tuple_element(IndexedElement(tuple_var, i))
                elements.extend(self.collect_all_tuple_elements(element))
            return elements

        return [tuple_var]
