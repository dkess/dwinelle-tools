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

local utils = require 'mp.utils'

function trim(s)
  -- from PiL2 20.4
  return (s:gsub("^%s*(.-)%s*$", "%1"))
end

function write_to_log(txt)
   f = io.open('rooms.txt', 'a')
   io.output(f)
   io.write(txt .. '\n')
   io.close(f)
   mp.osd_message('wrote to log')
end

function ypress()
   current_time = mp.get_property_number('time-pos')
   t = utils.subprocess({args = {'zenity', '--entry'}})
   room = trim(t.stdout)
   if room ~= '' then
      write_to_log(current_time .. ' ' .. room)
   end
end

mp.add_key_binding('i', ypress)
