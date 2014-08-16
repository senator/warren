import os, sys, pickle
from argparse import ArgumentParser
from glob import glob
from distutils.core import setup
from distutils.command.install import install as _install
from distutils.command.clean import clean as _clean

data_map_cache_file = ".setup_data_file_map_cache"

class MyParser(ArgumentParser):
    def print_usage(self, f=None):
        raise ValueError

    def print_help(self, f=None):
        raise ValueError

    def format_usage(self):
        raise ValueError

    def format_help(self):
        raise ValueError

def _post_install(setup_thing):
    pass

def _post_clean(setup_thing):
    try:
        os.unlink(data_map_cache_file)
    except OSError:
        pass

    os.system("rm -rf build")

class clean(_clean):
    def run(self):
        _clean.run(self)
        self.execute(_post_clean, (self,), msg="Running post clean task")

class install(_install):
    def run(self):
        _install.run(self)
        self.execute(_post_install, (self,),
                     msg="Running post install task")

def determine_setup_prefs():
    try:
        parser = MyParser()
        parser.add_argument('--share-dir', default='share', type=str,
                help='destination directory for data files')
        parser.add_argument('--conf-dir', default='etc', type=str,
                help='destination directory for configuration files')

        args, unknown = parser.parse_known_args()
        sys.argv = [sys.argv[0]] + unknown # important for setup()
    except ValueError:
        return {'share': 'share', 'conf': 'etc'}

    return {'share': args.share_dir, 'conf': args.conf_dir}

# Probably not the most efficient implementation possible.
def path_parts(path, parts):
    most, rest = os.path.split(path)
    if rest != '':
        parts.append(rest)
    if most != '' and most != os.path.sep:
        path_parts(most, parts)
    else:
        parts.reverse()

# Return 2-tuples of dest_dir+more and filenames within src_dir.
# I bet I could do some neat pythonic thing using yield here.
def prepare_share_data(dest_dir, src_dir):
    results = []

    for path, dirnames, filenames in os.walk(src_dir):
        parts = []
        path_parts(path, parts)
        dest_more = os.path.join(dest_dir, os.path.sep.join(parts[1:]))
        for f in filenames:
            results.append((dest_more, os.path.join(path, f)))

    result_map = {}
    for k,v in results:
        if k not in result_map:
            result_map[k] = []
        result_map[k].append(v)

    return result_map.items()

def get_data_file_map(directories):
    try:
        f = open(data_map_cache_file, "r")
        print "Loading data file map from cache ..."
        return pickle.load(f)
    except Exception:
        pass

    print "Determing installation structure of data files ..."

    data_file_map = [ (directories['conf'], glob('conf/*')) ]
    data_file_map.extend(prepare_share_data(directories['share'], 'share'))

    try:
        f = open(data_map_cache_file, "w")
        pickle.dump(data_file_map, f)
    except Exception:
        print "Could not cache data file map."

    return data_file_map

if __name__ == "__main__":
    directories = determine_setup_prefs()
    data_files = get_data_file_map(directories)

    setup(name='warren',
          version='0.01',
          author='Lebbeous Fogle-Weekley',
          author_email='lebbeous@gmail.com',
          description='A role-playing adventure game in an Americana-themed setting.',
          url='http://lebbeo.us/',
          package_dir={'': 'lib'},
          data_files=data_files,
          scripts=['bin/run-warren.py'],  # script can't have same name as pkg
          packages=['warren'],
          cmdclass={'install': install, 'clean': clean})
