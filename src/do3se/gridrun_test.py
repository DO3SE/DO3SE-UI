import numpy as np
from do3se.gridrun import get_coord_batches,INVALID_COORD

coords = np.array([
    [0,0],
    [0,1],
    [0,2],
    [1,0],
    [1,1],
])

def test_get_coord_batches():
    """Test get_coord_batches"""
    out = get_coord_batches(coords, 2)
    assert len(out) == 3
    assert len(out[0]) == 2
    # The output pads the coords to extend the last batch
    assert out.flatten().tolist() != coords.flatten().tolist()
    coord_i_count = len(coords.flatten())
    np.testing.assert_array_equal(out.flatten()[0:coord_i_count], coords.flatten()[0:coord_i_count])
    assert out[2][1][0] == INVALID_COORD
    assert out[2][1][1] == INVALID_COORD