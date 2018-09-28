import numpy as np

from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

import hdbscan
from .sklearn_optics import optics


def feature_scaling(photos_longlat, default_longlat):
    # Standard feature scaling.
    ########### TO DO : REPLACE WITH MANUAL RESCALING?? #############
    X = StandardScaler().fit_transform(photos_longlat)
    # Scale latitude features as a first approximation of great circle
    # distance.
    logitude_scaler = np.sin(default_longlat.latitude * np.pi / 180.)
    X[:, 0] *= logitude_scaler
    return X


def dbscan_clustering(photos_longlat, default_longlat):
    # Feature scaling.
    X = StandardScaler().fit_transform(photos_longlat, default_longlat)

    # https://github.com/alitouka/spark_dbscan/wiki/Choosing-parameters-of-DBSCAN-algorithm
    nbrs = NearestNeighbors(n_neighbors=2, algorithm='ball_tree').fit(X)
    distances, indices = nbrs.kneighbors(X)
    eps_min = 1e-4 * (np.mean([X[:, 0].max() - X[:, 0].min(),
                               X[:, 1].max() - X[:, 1].min()]))
    eps = np.max([eps_min, np.percentile(distances[:, 1], 90)])
    min_samples = int(0.01 * X.shape[0])

    # Use DBSCAN.
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(X)
    return db.labels_


def optics_clustering(photos_longlat, default_longlat, global_min_samples=10,
                      max_eps_scaling=1.):
    # Feature scaling.
    X = StandardScaler().fit_transform(photos_longlat, default_longlat)

    min_samples = max([global_min_samples, int(0.01 * X.shape[0])])
    max_eps = max_eps_scaling * np.mean([(X[:, 0].max() - X[:, 0].min()),
                                         (X[:, 1].max() - X[:, 1].min())])

    optcl = optics.OPTICS(min_samples=min_samples, max_eps=max_eps)
    optcl.fit(X)
    return optcl.labels_


def hdbscan_clustering(photos_longlat, default_longlat, global_min_samples=10,
                       min_samples_scaling=0.5):
    # Feature scaling.
    X = StandardScaler().fit_transform(photos_longlat, default_longlat)

    min_cluster_size = max([global_min_samples, int(0.01 * X.shape[0])])

    hdbcl = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size,
                            min_samples=int(min_samples_scaling *
                                            min_cluster_size))
    hdbresult = hdbcl.fit(X)
    return hdbresult.labels_
