from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import ast

try:
    import rhinoscriptsyntax as rs
except ImportError:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = ['FaceSelector', ]


class FaceSelector(object):

    @staticmethod
    def select_face(self, message="Select a face."):
        guid = rs.GetObject(message, preselect=True, filter=rs.filter.mesh | rs.filter.textdot)
        if guid:
            prefix = self.attributes['name']
            name = rs.ObjectName(guid).split('.')
            if 'face' in name:
                if not prefix or prefix in name:
                    key = name[-1]
                    key = ast.literal_eval(key)
                    return key
        return None

    @staticmethod
    def select_faces(self, message="Select faces."):
        keys = []
        guids = rs.GetObjects(message, preselect=True, filter=rs.filter.mesh | rs.filter.textdot)
        if guids:
            prefix = self.attributes['name']
            seen = set()
            for guid in guids:
                name = rs.ObjectName(guid).split('.')
                if 'face' in name:
                    if not prefix or prefix in name:
                        key = name[-1]
                        if not seen.add(key):
                            key = ast.literal_eval(key)
                            keys.append(key)
        return keys


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    pass
