#
#   Copyright 2020 The SpaceONE Authors.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from setuptools import setup, find_packages

with open('VERSION', 'r') as f: 
    VERSION = f.read().strip()
    f.close()

setup(
    name='kt-ds-inventory',
    version=VERSION,
    description='kt-ds inventory service',
    long_description='',
    url='',
    author='',
    author_email='',
    license='Apache License 2.0',
    packages=find_packages(),
    install_requires=[
        'kt-ds-core',
        'kt-ds-api',
        'mongoengine',
        'redis',
        'langcodes',
        'ipaddress',
        'python-consul',
        'fakeredis',
        'mongomock'
    ],
    zip_safe=False,
)
