# Copyright (C) 2014  Nicolas Jouanin
#
# This file is part of Repool.
#
# Repool is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Repool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Repool.  If not, see <http://www.gnu.org/licenses/>.


from setuptools import setup, find_packages

setup(
  name = "repool",
  version = "0.0.1",
  description="Connection pool for rethinkdb",
  author="Nicolas Jouanin",
  author_email='nicolas.jouanin@gmail.com',
  url="https://github.com/njouanin/repool",
  license='GPLv3',
  packages=find_packages(exclude=['tests']),
  classifiers=[
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 3.3',
    'Topic :: Database'
  ]
)
