from testpath import print_file_info
import sys
import os

print_file_info()

print('*' * 100)
# 方法1：使用os.path.abspath()
current_file = os.path.abspath(__file__)
print(f'current_file={current_file}')
print(f'__file__={__file__}')

# 方法2：使用sys.argv[0]
script_path = os.path.abspath(sys.argv[0])
print(f'script_path={script_path}')

# 获取文件所在目录
current_dir = os.path.dirname(current_file)
print(f'current_dir={current_dir}')

# 获取上一级目录
basedir = os.path.dirname(current_dir)
print(f'basedir={basedir}')