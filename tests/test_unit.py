from src import octvencode
import numpy as np
import pytest

class TestUnit:

    def test_homogeneity(self):
        volume1 = np.zeros(10)
        assert octvencode._is_volume_homogeneous(volume1)
        
        volume2 = np.zeros(10)
        volume2[3] = 1
        assert not octvencode._is_volume_homogeneous(volume2)
        
        volume3 = np.array([1])
        assert octvencode._is_volume_homogeneous(volume3)
        
        volume4 = np.array([])
        assert octvencode._is_volume_homogeneous(volume4)
        
        volume5 = "abcd"
        with pytest.raises(TypeError) as err1:
            octvencode._is_volume_homogeneous(volume5)
            assert err1.type == TypeError
        
        volume6 = np.zeros(1000)
        volume6.reshape((10,10,10))
        assert octvencode._is_volume_homogeneous(volume6)
        
        volume7 = np.zeros(1000)
        volume7[17] = 1
        volume7.reshape((10,10,10))
        assert not octvencode._is_volume_homogeneous(volume7)
        
    
    def test_reshaping(self):
        volume1 = np.zeros(1000)
        volume1_reshaped = octvencode._reshape_volume_to_cubic(volume1)
        assert volume1_reshaped.shape == (10,10,10)
        assert volume1_reshaped.size == volume1.size
        
        volume2 = np.zeros(999)
        with pytest.raises(ValueError) as err1:
            octvencode._reshape_volume_to_cubic(volume2)
            assert err1.type == ValueError
        
        volume3 = "abcd"
        with pytest.raises(TypeError) as err2:
            octvencode._reshape_volume_to_cubic(volume3)
            assert err2.type == TypeError
        