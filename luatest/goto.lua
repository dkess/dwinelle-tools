-- This file is part of dwinelle-tools.

-- dwinelle-tools is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.

-- dwinelle-tools is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.

-- You should have received a copy of the GNU General Public License
-- along with dwinelle-tools.  If not, see <http://www.gnu.org/licenses/>.

-- run with --script-opts=goto-pyscript=/path/to/mpv_goto.py
require 'mp.options'

options = {pyscript='DEFAULT'}
read_options(options, 'goto')
goto_script = options.pyscript
print('goto script '.. goto_script)

local utils = require 'mp.utils'

function ypress()
  if not mp.get_property_bool('pause') then
    mp.command('cycle pause')
  end
  t = utils.subprocess({args = {'zenity', '--entry'}})
  --clipid = mp.get_property('filename/no-ext')
  path = mp.get_property('path')
  print('path = '.. path)
  entry = t.stdout
  if entry ~= '' then
    --mp.command('seek ' .. entry .. ' absolute')
    py = utils.subprocess({args = {'python3', goto_script, path, entry}})
    print(py.stdout)
    print('---')
    for cmd in string.gmatch(py.stdout, '[^\n]+') do
      print(cmd)
      mp.command(cmd)
    end
  end
end

mp.add_key_binding('y', ypress)
