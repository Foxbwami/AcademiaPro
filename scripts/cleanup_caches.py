import os, shutil
root = os.getcwd()
print('workspace_root:', root)
to_delete_dirs = []
to_delete_files = []
for dirpath, dirnames, filenames in os.walk(root):
    for d in list(dirnames):
        if d in ('__pycache__', '.pytest_cache', '.cache'):
            to_delete_dirs.append(os.path.join(dirpath, d))
    for f in filenames:
        if f.endswith('.pyc'):
            to_delete_files.append(os.path.join(dirpath, f))
print('found_dirs:', len(to_delete_dirs))
for p in to_delete_dirs[:200]:
    print('DIR', p)
print('found_files:', len(to_delete_files))
for p in to_delete_files[:200]:
    print('FILE', p)

# delete
deleted_dirs = 0
deleted_files = 0
for p in to_delete_dirs:
    try:
        shutil.rmtree(p)
        deleted_dirs += 1
    except Exception as e:
        print('ERR_DEL_DIR', p, repr(e))
for p in to_delete_files:
    try:
        os.remove(p)
        deleted_files += 1
    except Exception as e:
        print('ERR_DEL_FILE', p, repr(e))

print('deleted_dirs:', deleted_dirs)
print('deleted_files:', deleted_files)

# remaining
remain_dirs = 0
remain_files = 0
for dirpath, dirnames, filenames in os.walk(root):
    for d in dirnames:
        if d in ('__pycache__', '.pytest_cache', '.cache'):
            remain_dirs += 1
    for f in filenames:
        if f.endswith('.pyc'):
            remain_files += 1
print('remaining_dirs:', remain_dirs)
print('remaining_files:', remain_files)
