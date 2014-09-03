from warren import archive_extension

from os.path import dirname, basename, join
from os import access, R_OK
from zipfile import ZipFile

class ResourceFinder(object):
    def __init__(self, data_root):
        self.data_root = data_root
        self.open_archives = {}

    def _find_in_most_specific_archive(self, path):
        file_name = basename(path)
        dir_name = dirname(path)

        while len(dir_name) > 0:
            archive_name = join(self.data_root, dir_name + archive_extension)

            if access(archive_name, R_OK) and \
                archive_name not in self.open_archives:
                self.open_archives[archive_name] = ZipFile(archive_name, "r")

            if self.open_archives[archive_name]:
                print "expecting to find file %s in archive %s" % \
                        (file_name, archive_name)
                return self.open_archives[archive_name].open(file_name)
                    # XXX open() method is for ZipFile; would be different for
                    # Tar if we want to change archive type.

            file_name = join(basename(dir_name), file_name)
            dir_name = dirname(dir_name)

        raise IOError(
            "File not found (%s), not even in archive; data_root is %s" % \
                    (path, self.data_root)
                    )

    def open_for_reading(self, path):
        try:
            return open(join(self.data_root, path), "r")
        except IOError:
            return self._find_in_most_specific_archive(path)

    def clear(self):
        self.open_archives.clear()

class ResourceManager(object):
    def __init__(self, resource_finder):
        self.resource_finder = resource_finder
        self.stash = {}

    def get(self, path, processor):
        if path not in self.stash:
            with self.resource_finder.open_for_reading(path) as f:
                self.stash[path] = processor(f)

        return self.stash[path]

    def clear(self, finder_too=False):
        self.stash.clear()
        if finder_too:
            self.resource_finder.clear()
