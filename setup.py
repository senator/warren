import os, sys
from argparse import ArgumentParser
from glob import glob
from distutils.core import setup
from distutils.command.install import install as _install
from distutils.command.clean import clean as _clean

class MyParserBailOut(RuntimeError):
    pass

class MyParser(ArgumentParser):
    def print_usage(self, f=None):
        raise MyParserBailOut

    def print_help(self, f=None):
        raise MyParserBailOut

    def format_usage(self):
        raise MyParserBailOut

    def format_help(self):
        raise MyParserBailOut

def _post_install(setup_thing):
    bin_script = os.path.join(setup_thing.install_scripts, 'run-warren.py')

    sed_subst = 's$PATH_OVERRIDE = None$PATH_OVERRIDE = "%s"$' % \
            os.path.abspath(setup_thing.install_lib)
    sed_cmd = "sed -i -e '%s' %s " % (sed_subst, bin_script)
    os.system("which sed > /dev/null && " + sed_cmd + " || "
        "echo 'sed failed; you may need to set PYTHONPATH to run warren.'")

    symlink = os.path.join(setup_thing.install_scripts, "warren")
    if not os.access(symlink, os.F_OK):
        os.symlink("run-warren.py", symlink)

def _post_clean(setup_thing):
    os.system("rm -rf build")

class clean(_clean):
    def run(self):
        _clean.run(self)
        self.execute(_post_clean, (self,), msg="Running post clean task")

class install(_install):
    def run(self):
        _install.run(self)
        self.execute(_post_install, (self,), msg="Running post install task")

def determine_setup_prefs():
    try:
        parser = MyParser()
        parser.add_argument('--share-dir', default='share', type=str,
                help='destination directory for data files')
        parser.add_argument('--conf-dir', default='etc', type=str,
                help='destination directory for configuration files')

        args, unknown = parser.parse_known_args()
        sys.argv = [sys.argv[0]] + unknown # important for setup()
    except MyParserBailOut:
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
    data_file_map = [ (directories['conf'], glob('conf/*')) ]

    if 'install' in sys.argv[1:]: # XXX other command where this matters?
        print "Determing installation structure of data files ..."

        data_file_map.extend(prepare_share_data(directories['share'], 'share'))

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
