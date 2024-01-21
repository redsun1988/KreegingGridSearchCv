import math
import numpy as np
import geopandas as gpd
from sklearn.svm import SVR
from libpysal import weights
from pykrige.rk import Krige
from esda.moran  import Moran
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted


class ErrorKrigeRegressionAdapter(BaseEstimator, RegressorMixin):

    def __init__(self, basic_regressor: BaseEstimator = SVR(), krige = Krige(), weightsParams: dict = {"type": "knn", "k": 5}, moranThreshold: float = 0.5):
        self.weightsParams: dict = weightsParams
        self.moranThreshold: float = moranThreshold
        self.basic_regressor: BaseEstimator = basic_regressor
        self.geometryColumn: str = 'geometry'
        self.krige: Krige = krige
        self.krige_is_fitted = False

    def _createWeights(self, featuries_copy: gpd.GeoDataFrame):
        if self.weightsParams["type"] == "knn":
            w = weights.KNN.from_dataframe(featuries_copy,
                                           k=self.weightsParams["k"], 
                                          )
            return w
        raise ValueError(f"""Such a weightsParams field value is not supported.
            {self.weightsParams}
        """)
    
    def _build_moran_over_errors(self, X, errors):
        featuries_copy = X.copy()
        featuries_copy["errors"] = errors

        w = self._createWeights(featuries_copy)
        self._moran = Moran(
            featuries_copy["errors"],
            w
        )
    
    def fit(self, X: gpd.GeoDataFrame, y):
        self.krige_is_fitted = False
        basic_regressor_input = X.loc[:, X.columns != self.geometryColumn]
        self.basic_regressor.fit(basic_regressor_input, y)
        predictions = self.basic_regressor.predict(basic_regressor_input)
        errors = y - predictions

        
        self._build_moran_over_errors(X, errors)
        if abs(self._moran.I) >= self.moranThreshold:        
            coords = np.array(list(X[self.geometryColumn].apply(lambda p: (p.centroid.x, p.centroid.y)).values))
            self.krige.fit(coords, errors)
            self.krige_is_fitted = True

        return self

    def predict(self, X):
        basic_regressor_input = X.loc[:, X.columns != self.geometryColumn]
        coords = np.array(list(X[self.geometryColumn].apply(lambda p: (p.centroid.x, p.centroid.y)).values))
        
        predictions = self.basic_regressor.predict(basic_regressor_input)
        if self.krige_is_fitted:
            predictions += self.krige.predict(coords)
        return  predictions