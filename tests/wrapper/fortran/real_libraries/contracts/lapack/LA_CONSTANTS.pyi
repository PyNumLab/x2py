sp: Final[Int32] = kind(1.0)

szero: Final[Float32] = 0

shalf: Final[Float32]

sone: Final[Float32] = 1

stwo: Final[Float32] = 2

sthree: Final[Float32] = 3

sfour: Final[Float32] = 4

seight: Final[Float32] = 8

sten: Final[Float32] = 10

czero: Final[Complex64]

chalf: Final[Complex64]

cone: Final[Complex64]

sprefix: String[1]

cprefix: String[1]

sulp: Final[Float32]

seps: Final[Float32]

ssafmin: Final[Float32]

ssafmax: Final[Float32] = sone / ssafmin

ssmlnum: Final[Float32] = ssafmin / sulp

sbignum: Final[Float32] = ssafmax * sulp

srtmin: Final[Float32] = sqrt(ssmlnum)

srtmax: Final[Float32] = sqrt(sbignum)

stsml: Final[Float32]

stbig: Final[Float32]

sssml: Final[Float32]

ssbig: Final[Float32]

dp: Final[Int32]

dzero: Final[Float64] = 0

dhalf: Final[Float64]

done: Final[Float64] = 1

dtwo: Final[Float64] = 2

dthree: Final[Float64] = 3

dfour: Final[Float64] = 4

deight: Final[Float64] = 8

dten: Final[Float64] = 10

zzero: Final[Complex128]

zhalf: Final[Complex128]

zone: Final[Complex128]

dprefix: String[1]

zprefix: String[1]

dulp: Final[Float64]

deps: Final[Float64]

dsafmin: Final[Float64]

dsafmax: Final[Float64] = done / dsafmin

dsmlnum: Final[Float64] = dsafmin / dulp

dbignum: Final[Float64] = dsafmax * dulp

drtmin: Final[Float64] = sqrt(dsmlnum)

drtmax: Final[Float64] = sqrt(dbignum)

dtsml: Final[Float64]

dtbig: Final[Float64]

dssml: Final[Float64]

dsbig: Final[Float64]
