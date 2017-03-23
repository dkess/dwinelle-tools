local utils = require 'mp.utils'

function trim(s)
  -- from PiL2 20.4
  return (s:gsub("^%s*(.-)%s*$", "%1"))
end

function ypress()
  if not mp.get_property_bool('pause') then
    mp.command('cycle pause')
  end
  t = utils.subprocess({args = {'zenity', '--entry'}})
  entry = trim(t.stdout)
  if entry ~= '' then
    mp.command('seek ' .. entry .. ' absolute')
  end
end

mp.add_key_binding('y', ypress)
