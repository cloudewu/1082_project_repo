import os
import shutil as sh
from fnmatch import fnmatch

def ensure_dir_exists(dir_path, verbose=False, logger=None):
    if dir_path == '':
        return
    if os.path.isdir(dir_path):
        return
    dirname, basename = os.path.split(dir_path)
    ensure_dir_exists(dirname)
    os.mkdir(dir_path)
    if verbose:
        print(f'[ INFO ] mkdir {dir_path}')
    if logger:
        logger.write(f'mkdir {dir_path}')
    return

def copy_tree(pattern, current_path, source_dir, dest_dir, verbose=False, logger=None):
    source_path = os.path.normpath(os.path.join(source_dir, current_path))
    dest_path = os.path.normpath(os.path.join(dest_dir, current_path))

    for name in os.listdir(source_path):
        src = os.path.join(source_path, name)
        dst = os.path.join(dest_path, name)
        if os.path.isdir(src):
            next_path = os.path.join(current_path, name)
            copy_tree(pattern, next_path, source_dir, dest_dir, verbose=verbose, logger=logger)
        elif os.path.isfile(src) and fnmatch(name, pattern):
            ensure_dir_exists(dest_path, verbose=verbose, logger=logger)
            sh.copyfile(src, dst)
            if verbose:
                print(f'[ INFO ] cp {src} {dst}')
            if logger:
                logger.write(f'cp {src} {dst}\n')

def collect_files(pattern, source_dir, dest_dir, verbose=False, logger=None):
    from glob import glob

    files = glob(os.path.join(source_dir, '**', pattern), recursive=True)
    ensure_dir_exists(dest_dir)
    for filename in files:
        dst_path = os.path.join(dest_dir, os.path.basename(filename))
        sh.copyfile(filename, dst_path)
        if verbose:
            print(f'[ INFO ] cp {filename} {dst_path}')
        if logger:
            logger.write(f'cp {filename} {dst_path}\n')
    return

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('pattern', help='file pattern')
    parser.add_argument('source_dir', help='search target folder')
    parser.add_argument('dest_dir', help='copy destination')
    parser.add_argument('-l', '--log', help='write log info to file')
    parser.add_argument('-s', '--structured', action='store_true', help='copy files with directory structure')
    parser.add_argument('-v', '--verbose', action='store_true', help='print copy messages')
    args = parser.parse_args()

    logger = open(args.log, 'w+', encoding='utf-8') if args.log else None
    if args.structured:
        copy_tree(args.pattern, '.', args.source_dir, args.dest_dir, verbose=args.verbose, logger=logger)
    else:
        collect_files(args.pattern, args.source_dir, args.dest_dir, verbose=args.verbose, logger=logger)
    if logger:
        logger.close()