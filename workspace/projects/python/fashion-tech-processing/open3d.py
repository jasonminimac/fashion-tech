"""Mock open3d for testing pipeline logic on Python 3.14."""

import numpy as np


class Vector3dVector:
    """Mock vector container."""
    def __init__(self, data):
        self.data = np.asarray(data)
    
    def __len__(self):
        return len(self.data)


class PointCloud:
    """Mock point cloud."""
    def __init__(self):
        self.points = None
        self.colors = None
        self.normals = None
    
    def has_colors(self):
        return self.colors is not None
    
    def has_normals(self):
        return self.normals is not None
    
    def estimate_normals(self, search_param=None):
        """Mock normal estimation."""
        if self.points is None:
            raise ValueError("No points")
        self.normals = np.random.randn(*self.points.data.shape)
        
    def voxel_down_sample(self, voxel_size):
        """Mock downsampling."""
        if self.points is None:
            raise ValueError("No points")
        # Randomly keep some points
        mask = np.random.rand(len(self.points.data)) > 0.5
        new_pcd = PointCloud()
        new_pcd.points = Vector3dVector(self.points.data[mask])
        if self.colors is not None:
            new_pcd.colors = Vector3dVector(self.colors.data[mask])
        return new_pcd
    
    def remove_statistical_outliers(self, nb_neighbors=20, std_ratio=2.0):
        """Mock outlier removal."""
        if self.points is None:
            raise ValueError("No points")
        # Keep 80% of points
        mask = np.random.rand(len(self.points.data)) > 0.2
        new_pcd = PointCloud()
        new_pcd.points = Vector3dVector(self.points.data[mask])
        if self.colors is not None:
            new_pcd.colors = Vector3dVector(self.colors.data[mask])
        return new_pcd, mask
    
    def select_by_index(self, indices):
        """Mock index selection."""
        new_pcd = PointCloud()
        if self.points is not None:
            new_pcd.points = Vector3dVector(self.points.data[indices])
        if self.colors is not None:
            new_pcd.colors = Vector3dVector(self.colors.data[indices])
        return new_pcd


class TriangleMesh:
    """Mock triangle mesh."""
    def __init__(self):
        self.vertices = []
        self.triangles = []
        self.vertex_colors = None
    
    @staticmethod
    def create_from_point_cloud_poisson(pcd, depth=9, width=0, linear_fit=False):
        """Mock Poisson reconstruction."""
        mesh = TriangleMesh()
        # Simulate mesh generation
        n_vertices = max(100, len(pcd.points.data) // 5)
        mesh.vertices = np.random.randn(n_vertices, 3)
        mesh.triangles = np.random.randint(0, n_vertices, (n_vertices // 2, 3))
        densities = np.random.rand(n_vertices)
        return mesh, densities
    
    def remove_vertices_by_mask(self, mask):
        """Mock vertex removal."""
        keep_indices = np.where(~mask)[0]
        self.vertices = self.vertices[keep_indices]
    
    def remove_degenerate_triangles(self):
        """Mock degenerate removal."""
        pass
    
    def remove_unreferenced_vertices(self):
        """Mock unreferenced removal."""
        pass
    
    def compute_vertex_normals(self):
        """Mock normal computation."""
        pass


class KDTreeSearchParamHybrid:
    """Mock search parameter."""
    def __init__(self, radius=0.1, max_nn=30):
        self.radius = radius
        self.max_nn = max_nn


class geometry:
    """Mock geometry module."""
    PointCloud = PointCloud
    TriangleMesh = TriangleMesh
    KDTreeSearchParamHybrid = KDTreeSearchParamHybrid


class io:
    """Mock io module."""
    @staticmethod
    def read_point_cloud(path):
        """Mock read."""
        pcd = PointCloud()
        pcd.points = Vector3dVector(np.random.randn(1000, 3))
        pcd.colors = Vector3dVector(np.random.rand(1000, 3))
        return pcd
    
    @staticmethod
    def write_triangle_mesh(path, mesh, write_ascii=False):
        """Mock write."""
        pass


class utility:
    """Mock utility module."""
    Vector3dVector = Vector3dVector


# Module exports
__all__ = ["geometry", "io", "utility", "PointCloud", "TriangleMesh"]
