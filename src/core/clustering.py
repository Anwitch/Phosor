"""Clustering logic for face embeddings."""

import logging
import numpy as np
from sklearn.cluster import DBSCAN, KMeans
from collections import defaultdict

from core.models import FaceRecord, ClusterSummary

logger = logging.getLogger(__name__)


def cluster_faces(
    faces: list[FaceRecord],
    method: str = "dbscan",
    eps: float = 0.5,
    min_samples: int = 3,
    n_clusters: int = 10,
) -> list[FaceRecord]:
    """Cluster faces based on embedding similarity.

    Args:
        faces: List of FaceRecord with embeddings.
        method: Clustering method ("dbscan" or "kmeans").
        eps: DBSCAN epsilon parameter.
        min_samples: DBSCAN minimum samples parameter.
        n_clusters: KMeans number of clusters.

    Returns:
        Updated list of FaceRecord with cluster_id assigned.
    """
    if not faces:
        logger.warning("No faces to cluster")
        return []

    # Build embedding matrix
    embeddings = np.array([face.embedding for face in faces])

    # Perform clustering
    if method == "dbscan":
        clusterer = DBSCAN(eps=eps, min_samples=min_samples, metric="cosine")
        labels = clusterer.fit_predict(embeddings)
    elif method == "kmeans":
        clusterer = KMeans(n_clusters=n_clusters, random_state=42)
        labels = clusterer.fit_predict(embeddings)
    else:
        raise ValueError(f"Unknown clustering method: {method}")

    # Assign cluster IDs to faces
    for face, label in zip(faces, labels):
        face.cluster_id = int(label)

    num_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    num_noise = list(labels).count(-1)
    logger.info(
        f"Clustering complete: {num_clusters} clusters, {num_noise} noise points"
    )

    return faces


def build_cluster_summary(faces: list[FaceRecord]) -> list[ClusterSummary]:
    """Build summary statistics for each cluster.

    Args:
        faces: List of FaceRecord with cluster_id assigned.

    Returns:
        List of ClusterSummary objects.
    """
    cluster_data = defaultdict(list)

    # Group faces by cluster
    for face in faces:
        if face.cluster_id is not None and face.cluster_id >= 0:
            cluster_data[face.cluster_id].append(face)

    summaries = []
    # Use sequential numbering for labels (1, 2, 3...) instead of cluster_id
    for label_index, cluster_id in enumerate(sorted(cluster_data.keys()), start=1):
        cluster_faces = cluster_data[cluster_id]
        
        # Get unique image paths (first 3 as samples)
        unique_images = list(dict.fromkeys([f.image_path for f in cluster_faces]))
        sample_images = unique_images[:3]

        label = f"Person_{label_index:02d}"
        
        summary = ClusterSummary(
            cluster_id=cluster_id,
            label=label,
            num_faces=len(cluster_faces),
            sample_images=sample_images,
        )
        summaries.append(summary)

    logger.info(f"Built {len(summaries)} cluster summaries")
    return summaries
