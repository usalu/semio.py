from semio import PointOfViewParser
from numpy import array
from numpy.testing import assert_array_almost_equal
from pytest import mark

decimalPrecision = 2

@mark.parametrize('o, expectedVector',
[
    (0,[0,0,0]),
    (1,[1,0,0]),
    (4586.234,[4586.234,0,0]),
    (-7867.279,[-7867.279,0,0]),
    ('0',[0,0,0]),
    ('1',[1,0,0]),
    ('567.9874',[567.9874,0,0]),
    ('-9464.08',[-9464.08,0,0]),
    # ('X:-9464.08',[-9464.08,0,0]),
    # ('Y : 875.68',[0,875.68,0]),
    # ('z :   2847',[0,0,2847]),
    # ('{X : 567.7 , Y : 875.68 }',[0,875.68,0]),
    # ('z :   2847',[0,0,2847]),
    # ('123,2847',[123,2847,0]),
    # (',',[0,0,0]),
    # (',,',[0,0,0]),
    # (',,-6.43',[0,0,-6.43]),
    # ('4,54;-4847,676 ; -6.43',[4.54,-4847.676,-6.43]),
    # ('{ 4,54;-4847,676 ; }',[4.54,-4847.676,0]),
])
def test_parsers_PointOfViewParser_get_singleArgument(o,expectedVector): # TODO accept more formats
    assert_array_almost_equal(array(PointOfViewParser.get(o)), array(expectedVector),decimal=decimalPrecision)
    assert_array_almost_equal(array(PointOfViewParser.get((o))), array(expectedVector),decimal=decimalPrecision)
    assert_array_almost_equal(array(PointOfViewParser.get([o])), array(expectedVector),decimal=decimalPrecision)

# TODO test_PointOfViewParser.get_twoArguments
# TODO test_PointOfViewParser.get_threeArguments


# @mark.parametrize('o, expectedVector',
# [
#     (0,[0,0,0]),
#     (1,[1,0,0]),
#     (4586.234,[4586.234,0,0]),
#     (-7867.279,[-7867.279,0,0]),
#     ('0',[0,0,0]),
#     ('1',[1,0,0]),
#     ('567.9874',[567.9874,0,0]),
#     ('-9464.08',[-9464.08,0,0]),
#     # ('X:-9464.08',[-9464.08,0,0]),
#     # ('Y : 875.68',[0,875.68,0]),
#     # ('z :   2847',[0,0,2847]),
#     # ('{X : 567.7 , Y : 875.68 }',[0,875.68,0]),
#     # ('z :   2847',[0,0,2847]),
#     # ('123,2847',[123,2847,0]),
#     # (',',[0,0,0]),
#     # (',,',[0,0,0]),
#     # (',,-6.43',[0,0,-6.43]),
#     # ('4,54;-4847,676 ; -6.43',[4.54,-4847.676,-6.43]),
#     # ('{ 4,54;-4847,676 ; }',[4.54,-4847.676,0]),
# ])
# def test_parsers_ViewParser_singleArgument(o,expectedVector):
#     assert_array_almost_equal(array(PointOfViewParser.get(o)), array(expectedVector),decimal=decimalPrecision)
#     assert_array_almost_equal(array(PointOfViewParser.get((o))), array(expectedVector),decimal=decimalPrecision)
#     assert_array_almost_equal(array(PointOfViewParser.get([o])), array(expectedVector),decimal=decimalPrecision)

# TODO test_parsers_ViewParser_twoArguments
# TODO test_parsers_ViewParser_threeArguments
# TODO test_parsers_ViewParser_fourArguments


