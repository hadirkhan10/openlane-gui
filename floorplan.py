def set_rel_floorplan(core_util, file):
    file.write('set ::env(FP_SIZING) relative\n')
    file.write(f'set ::env(FP_CORE_UTIL) {core_util}\n')

def set_abs_floorplan(x0, y0, x1, y1, file):
    file.write('set ::env(FP_SIZING) absolute\n')
    file.write(f'set ::env(DIE_AREA) "{x0} {y0} {x1} {y1}"\n')