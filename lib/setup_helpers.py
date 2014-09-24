import os, sys, glob
from argparse import ArgumentParser
from distutils.command.install import install as _install
from distutils.command.build import build as _build
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

class SharePacker(object):
    def __init__(self, archive_ext, dest_dir, src_dir):
        self._plan = None
        self.archive_ext = archive_ext
        self.src_dir = src_dir
        self.dest_dir = dest_dir

    def ready(self):
        for f in self.plan()[0][1]:
            if not os.access(f, os.R_OK):
                return False
        return True

    def _generate_plan(self, dest_dir, src_dir):
        pkgfiles = []
        for f in os.listdir(src_dir):
            f = os.path.join(src_dir, f)
            if f.endswith(self.archive_ext):
                continue # don't plan to pack and repack archives
            elif os.path.isdir(f):
                pkgfiles.append(f + self.archive_ext)
            else:
                pkgfiles.append(f) # install plain files if any at this level

        return [(dest_dir, pkgfiles)] # return in this format for setup()

    def plan(self, rebuild=False):
        if self._plan is None or rebuild:
            self._plan = self._generate_plan(self.dest_dir, self.src_dir)

        return self._plan

    def pack(self):
        for f in self.plan()[0][1]:
            if f.endswith(self.archive_ext):
                archive_name = os.path.basename(f)
                dir_name = f.replace(self.archive_ext, "")

                # XXX This is very UNIX specific and requires both a) a zip
                # command that acts like we expect and b) modern bash or zsh.
                # These may be widely consistent on modern
                # Linux and Mac OS X but certainly are not guaranteed.
                # XXX we should build in another dir so as not to have to
                # avoid packing and repacking our archives
                print "Building archive: %s" % archive_name
                cmd = "cd %s && zip -q -u -z -0 -x '*%s' -r ../%s * <<<'WOR!'" \
                        % (dir_name, self.archive_ext, archive_name)
                os.system(cmd)

class build(_build):
    def run(self):
        _build.run(self)
        self.execute(self._post_build, (), msg="Running post build task")

    def _post_build(self):
        if self.prefs['pack_resources']:
            self.share_packer.pack()

class clean(_clean):
    def run(self):
        _clean.run(self)
        self.execute(self._post_clean, (), msg="Running post clean task")

    def _post_clean(self):
        os.system("""rm -rf build;
            find share -name '*%s' -delete;
            rm -f install.log""" % clean.archive_extension)


class install(_install):
    _install.user_options.extend([
            ('conf-dir=', None, 'Set target directory for configuration files'),
            ('share-dir=', None, 'Set target directory for data files')
            ])

    def run(self):
        _install.run(self)
        self.execute(self._post_install, (), msg="Running post install task")

    def _make_run_symlink(self):
        symlink = os.path.join(self.install_scripts, 'warren')
        try:
            os.unlink(symlink)
        except OSError:
            pass
        os.symlink('run-warren.py', symlink)

        if self.record:
            with open(self.record, 'a') as rf:
                print "One more update to '%s'" % self.record
                rf.write(symlink + "\n")

    def _hack_run_script(self):
        bin_script = os.path.join(self.install_scripts, 'run-warren.py')

        sed_subst = 's$PATH_OVERRIDE = None$PATH_OVERRIDE = "%s"$' % \
                os.path.abspath(self.install_lib)
        sed_subst += \
                ';s$DEFAULT_SHARE_PATH = None$DEFAULT_SHARE_PATH = "%s"$' % \
                os.path.abspath(os.path.join(self.install_data, self.prefs['share'], 'warren'))

        sed_cmd = "sed -i -e '%s' %s " % (sed_subst, bin_script)
        os.system("which sed > /dev/null && " + sed_cmd + " || "
            "echo 'sed failed; you may need to set PYTHONPATH to run warren.'")

    def _post_install(self):
        self._hack_run_script()
        self._make_run_symlink()

def determine_setup_prefs():
    results = {'share': 'share', 'conf': 'etc', 'pack_resources': False}

    # We don't have help= keyword arguments to add_argument() below because
    # we don't let argparser control this script's usage/--help output.  We
    # add that to distutils/setup's help output instead.
    try:
        parser = MyParser()
        parser.add_argument('--share-dir', default=results['share'], type=str)
        parser.add_argument('--conf-dir', default=results['conf'], type=str)
        parser.add_argument('--pack-resources',
            default=results['pack_resources'], action='store_true',
            help='make archives of resources before installing to share-dir')

        args, unknown = parser.parse_known_args()
        sys.argv = [sys.argv[0]] + unknown # important for setup()
    except MyParserBailOut:
        return results

    results['share'] = args.share_dir
    results['conf'] = args.conf_dir
    results['pack_resources'] = args.pack_resources
    return results

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

def get_data_file_map(prefs, share_packer):
    data_file_map = [ (prefs['conf'], glob.glob('conf/*')) ]

    if 'install' in sys.argv[1:]: # XXX other command where this matters?
        if prefs['pack_resources'] or share_packer.ready():
            print "Planning to install packed (archived) resources ..."
            data_file_map.extend(share_packer.plan())
        else:
            print "Determing installation structure of data files ..."
            data_file_map.extend(prepare_share_data(prefs['share'], 'share'))

    return data_file_map
