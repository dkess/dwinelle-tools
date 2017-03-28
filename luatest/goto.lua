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
