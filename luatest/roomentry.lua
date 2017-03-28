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
