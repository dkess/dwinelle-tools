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

-- To run this script with mpv, add options
-- --script=walking.lua --script-opts=walking-nodesfile=<FILE>,offset=<TIME>
-- where <FILE> is the nodesfile and <TIME> is the unix time in seconds when
-- the video started

--[[
require 'mp.options'

options = {}
read_options(options, 'walking')
offset = options.offset
if offset == -1 then
   print('WARNING: no offset specified! this could be very bad')
end
local file = io.open(options.path)
local s = f:read('*a')
f:close()
nodes = utils.parse_json(s)
--]]

function write_to_log(txt)
   f = io.open('walkinglog.txt', 'a')
   io.output(f)
   io.write(txt .. '\n')
   io.close(f)
   mp.osd_message('wrote to log')
end

function ypress()
   current_time = mp.get_property_number('time-pos')
   write_to_log('y ' .. current_time)
end

function ipress()
   current_time = mp.get_property_number('time-pos')
   write_to_log('i ' .. current_time)
end

mp.add_key_binding('y', ypress)
mp.add_key_binding('i', ipress)
