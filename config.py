def set_design_name(name, file):
    file.write(f'set ::env(DESIGN_NAME) {name}\n')

def set_clock_definition(clk_port, clk_period, file):
    file.write(f'set ::env(CLOCK_PERIOD) "{clk_period}"\n')
    file.write(f'set ::env(CLOCK_PORT) "{clk_port}"\n')

def set_no_clock(file):
    file.write(f'set ::env(CLOCK_TREE_SYNTH) 0\n')
    file.write(f'set ::env(CLOCK_PORT) ""\n')