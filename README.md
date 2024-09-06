A small extension over pykrige to support GridSearchCV and automatically fit the krige model over regression's model error. The ErrorKrigeRegressionAdapter is used to combine a regression class and Krige. 
The [Krige model]([url](https://en.wikipedia.org/wiki/Kriging)) is calculated over the besic_regressor errors if errors have geo correlation. The geo correlation is calculated automatically via a Moran value.

**basic_regressor** - the basic regressor model that you would like to use 

**weightsParams** - weights are used to calculated geo neibors for Moran (only the knn algorithm is implemented) 

**moranThreshold** - if a Moran value is less that this threshold Krige will not be used
```python
krigeAdapter = ErrorKrigeRegressionAdapter(basic_regressor)

basic_param_grid = [{
    "basic_regressor__reg__n_estimators": [150, 300, 450],
    'moranThreshold': [0.1, 0.5],
    'krige__n_closest_points': [1, 2, 3, 5],
    'weightsParams': [{'type': 'knn', 'k': 5}, {'type': 'knn', 'k': 4}]
}]

estimator = GridSearchCV(krigeAdapter, basic_param_grid, cv=5, n_jobs=-1)
estimator.fit(X, y)
estimator.best_score_
```
All classes are located in the krigeExtrenstions.py local file. So you suppose to keep it locally during import.
```python
from krigeExtrenstions import ErrorKrigeRegressionAdapter
```
You also suppose to have several extra packages installed:
```
[numpy]([url](https://numpy.org/install/))
[PySAL](https://pysal.org/esda/)
[pykrige]([url](https://geostat-framework.readthedocs.io/projects/pykrige/en/stable/))
[geopandas]([url](https://geopandas.org/en/stable/getting_started/install.html))
[scikit-learn]([url](https://scikit-learn.org/stable/install.html))
```

See grid_search_cv_ex.ipynb to test a basic sample. 

By default, geo objects should be stored in the "geometry" column. You can specify a custom column via the geometryColumn field
X for the fit method should have the GeoDataFrame type.
