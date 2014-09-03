import os, sys
from distutils.core import setup

def cd_to_script_location():
    """ Some things will work better if we can just be sure our CWD is the same
        one as where the setup.py script lives. """
    script_name = __file__
    if not os.path.isabs(script_name):
        script_name = os.path.join(os.getcwd(), script_name)

    if not os.access(script_name, os.R_OK):
        raise OSError("Couldn't find path of script - not %s !?" % script_name)
    else:
        os.chdir(os.path.dirname(script_name))

if __name__ == "__main__":
    cd_to_script_location()
    sys.path.insert(0, "lib")
    import warren
    from setup_helpers import *
    clean.archive_extension = warren.archive_extension
    print "Setup for Warren v%s" % warren.version

    prefs = determine_setup_prefs()
    share_packer = SharePacker(warren.archive_extension,
            os.path.join(prefs['share'], 'warren'), 'share/warren')
    data_files = get_data_file_map(prefs, share_packer)

    build.prefs = prefs
    build.share_packer = share_packer
    install.prefs = prefs

    setup(name='warren',
          version=warren.version,
          author='Lebbeous Fogle-Weekley',
          author_email='lebbeous@gmail.com',
          description='A role-playing adventure game in an Americana-themed setting.',
          url='http://lebbeo.us/',
          package_dir={'': 'lib'},
          data_files=data_files,
          scripts=['bin/run-warren.py'],  # script can't have same name as pkg
          packages=['warren', 'warren.entities', 'warren.conversations'],
          cmdclass={'install': install, 'clean': clean, 'build': build})
