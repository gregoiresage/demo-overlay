#
# This file is the default set of rules to compile a Pebble application.
#
# Feel free to customize this to your needs.
#
import os.path

top = '.'
out = 'build'


def options(ctx):
    ctx.load('pebble_sdk')


def configure(ctx):
    """
    This method is used to configure your build. ctx.load(`pebble_sdk`) automatically configures
    a build for each valid platform in `targetPlatforms`. Platform-specific configuration: add your
    change after calling ctx.load('pebble_sdk') and make sure to set the correct environment first.
    Universal configuration: add your change prior to calling ctx.load('pebble_sdk').
    """
    ctx.load('pebble_sdk')

from waflib import TaskGen, Node
from waflib.TaskGen import before_method,feature
import string
import json
import re
from subprocess import Popen,PIPE
 
def generate_ld_tpl_ovl(task):
    template_script = open( task.inputs[0].abspath() ,'r' )
    overlays_json = open( task.inputs[1].abspath() ,'r' )
    ldscript = open( task.outputs[0].abspath() ,'w' )
    overlay_header = open( task.outputs[1].abspath() ,'w' )
 
    ovl_content = ''
    ovl_table = ''
 
    firstoverlay_name = ''
    overlay_name = ''
 
    overlay_header.write('typedef enum {\n')
 
    overlays=json.load(overlays_json)
 
    for idx, overlay in enumerate(overlays['overlays']):
 
        overlay_name = overlay['name']
 
        ovl_content = ovl_content + '\t\t'+overlay_name+'_ovl\n'
        ovl_content = ovl_content + '\t\t{\n'
 
        for fileName in overlay['files'] :
            ovl_content = ovl_content + '\t\t\t*/'+fileName+'*(.text)\n'
            ovl_content = ovl_content + '\t\t\t*/'+fileName+'*(.text.*)\n'
            ovl_content = ovl_content + '\t\t\t*/'+fileName+'*(.rodata)\n'
            ovl_content = ovl_content + '\t\t\t*/'+fileName+'*(.rodata*)\n'
            ovl_content = ovl_content + '\t\t\t*/'+fileName+'*(.data.*)\n'
            ovl_content = ovl_content + '\t\t\t*/'+fileName+'*(.bss)\n'
            ovl_content = ovl_content + '\t\t\t*/'+fileName+'*(.bss*)\n'
 
        ovl_content = ovl_content + '\t\t}\n'
 
        if(firstoverlay_name == ''):
            ovl_table = '\t\t\tLONG(0);\n'
            firstoverlay_name = overlay_name
        else:
            ovl_table = ovl_table + '\t\t\tLONG(LOADADDR('+overlay_name+'_ovl) - LOADADDR('+firstoverlay_name+'_ovl));\n'
        ovl_table = ovl_table + '\t\t\tLONG(SIZEOF(' + overlay_name +'_ovl));\n'
 
        overlay_header.write('\t' + overlay_name.upper() + '_OVL,\n')
 
    overlay_header.write('} OverlayId;\n')

    overlay_header.write('#define NUM_OVERLAYS ' + str(len(overlays['overlays'])))
 
    values = {'OVL_CONTENT' : ovl_content, 'OVL_TABLE' : ovl_table}
 
    for line in template_script:
        line = string.Template(line)
        line = line.safe_substitute(values)
        ldscript.write(line)
 
def generate_default_ld_script(task):
    template_script = open( task.inputs[0].abspath() ,'r' )
    ldscript = open( task.outputs[0].abspath() ,'w' )
 
    values = {
        'STRT_ORIGIN'   : '0',
        'STRT_LENGTH'   : '0x8000',
        'APP_ORIGIN'    : '0x8000',
        'APP_LENGTH'    : '0x7000',
        'OVERLAY_AT'    : '0xF000'
    }
 
    for line in template_script:
        line = string.Template(line)
        line = line.substitute(values)
        ldscript.write(line)
 
def get_app_length(elf_file):
    app_length=0
    readelf_process=Popen(['arm-none-eabi-readelf','-SW',elf_file],stdout=PIPE)
    readelf_output=readelf_process.communicate()[0]
    if not readelf_output:
        raise InvalidBinaryError()
    app_start=0
    for line in readelf_output.splitlines():
        if len(line)<10:
            continue
        line=line[6:]
        columns=line.split()
        if columns[0]=='.text2' :
            app_start = int(columns[2],16)
        elif columns[0] in ['.data', '.got', '.got.plt', '.bss']:
            app_length = int(columns[2],16) + int(columns[4],16) - app_start
    # app_length += 0x100 - (app_length % 0x100) # 0x100 alignment
    return app_length
 
def get_strt_length(elf_file):
    strt_length=0
    readelf_process=Popen(['arm-none-eabi-readelf','-SW',elf_file],stdout=PIPE)
    readelf_output=readelf_process.communicate()[0]
 
    if not readelf_output:
        raise InvalidBinaryError()
    for line in readelf_output.splitlines():
        if len(line)<10:
            continue
        line=line[6:]
        columns=line.split()
        if columns[0].endswith("_ovl") and not columns[0].startswith(".") :
            strt_length = max(strt_length, int(columns[4],16))
    strt_length += 0x82+0x26;
    strt_length += 0x100 - (strt_length % 0x100) # 0x100 alignment
    return strt_length
 
def get_overlay_address(elf_file):
    strt_length = get_strt_length(elf_file)
    app_length  = get_app_length(elf_file)
    return (strt_length + app_length)
 
def generate_final_ld_script(task):
    template_script = open( task.inputs[0].abspath() ,'r' )
    ldscript = open( task.outputs[0].abspath() ,'w' )
 
    strt_length = get_strt_length(task.inputs[1].abspath())
    app_origin = strt_length
    app_length = get_app_length(task.inputs[1].abspath())
    overlay_at = get_overlay_address(task.inputs[1].abspath())
 
    print "STRT_LENGTH = " + str(hex(strt_length))
    print "APP_LENGTH = " + str(hex(app_length))
    print "OVERLAY_AT = " + str(hex(overlay_at))
 
    values = {
        'STRT_ORIGIN'   : '0',
        'STRT_LENGTH'   : str(hex(strt_length)),
        'APP_ORIGIN'    : str(hex(app_origin)),
        'APP_LENGTH'    : str(hex(app_length)),
        'OVERLAY_AT'    : str(hex(overlay_at))
    }
 
    for line in template_script:
        line = string.Template(line).substitute(values)
        ldscript.write(line)

def extract_ovl_sections(task):
    def extract_section(elf_file, offset, size):
        elf = open(elf_file,'rb')
        elf.seek(offset)
        with open('resources/data/OVL.bin', "ab") as f:
            data = elf.read(size)
            f.write(data)

    def extract_sections(elf_file):
        readelf_process=Popen(['arm-none-eabi-readelf','-SW',elf_file],stdout=PIPE)
        readelf_output=readelf_process.communicate()[0]
        if not readelf_output:
            raise InvalidBinaryError()
        for line in readelf_output.splitlines():
            if len(line)<10:
                continue
            line=line[6:]
            columns=line.split()
            if columns[0].endswith("_ovl") and not columns[0].startswith(".") :
                extract_section(elf_file, int(columns[3],16), int(columns[4],16))

    with open('resources/data/OVL.bin', "wb") as f:
            f.write('')

    extract_sections(task.inputs[0].abspath())

def build(ctx):
    ctx.load('pebble_sdk')

    build_worker = os.path.exists('worker_src')
    binaries = []

    cached_env = ctx.env
    for platform in ctx.env.TARGET_PLATFORMS:
        ctx.env = ctx.all_envs[platform]
        ctx.set_group(ctx.env.PLATFORM_NAME)

        # generate the ld script template with overlay sections
        ctx(
            rule    = generate_ld_tpl_ovl,
            source  = ['pebble_app.ld.tpl', 'overlays.json'],
            target  = ['{}/pebble_app_ovl.ld.tpl'.format(ctx.env.BUILD_DIR),'overlays.h']
        )

        # generate the default ld script
        ctx(
            rule    = generate_default_ld_script,
            source  = '{}/pebble_app_ovl.ld.tpl'.format(ctx.env.BUILD_DIR),
            target  = '{}/pebble_app_default.ld'.format(ctx.env.BUILD_DIR)
        )

        # compile the first elf with the default ldscript
        app_comp_elf = '{}/pebble-app_comp.elf'.format(ctx.env.BUILD_DIR)
        ctx.pbl_build(source=ctx.path.ant_glob('src/c/**/*.c'), 
            target=app_comp_elf, 
            bin_type='app',
            ldscript='build/{}/pebble_app_default.ld'.format(ctx.env.BUILD_DIR)
            )

        # generate the final ld script
        ctx(
            rule    = generate_final_ld_script,
            source  = ['{}/pebble_app_ovl.ld.tpl'.format(ctx.env.BUILD_DIR),app_comp_elf],
            target  = '{}/pebble_app_final.ld'.format(ctx.env.BUILD_DIR)
        )

        # if the binary files have changed after the extraction, at this time the program resources
        # are not good, we must call the script one more time to have a correct generated final .pbw
        app_elf = '{}/pebble-app.elf'.format(ctx.env.BUILD_DIR)
        ctx.pbl_build(source=ctx.path.ant_glob('src/c/**/*.c'), 
            target=app_elf, 
            bin_type='app',
            ldscript='build/{}/pebble_app_final.ld'.format(ctx.env.BUILD_DIR)
            )

        if build_worker:
            worker_elf = '{}/pebble-worker.elf'.format(ctx.env.BUILD_DIR)
            binaries.append({'platform': platform, 'app_elf': app_elf, 'worker_elf': worker_elf})
            ctx.pbl_build(source=ctx.path.ant_glob('worker_src/c/**/*.c'),
                          target=worker_elf,
                          bin_type='worker')
        else:
            binaries.append({'platform': platform, 'app_elf': app_elf})

        # extract the binary overlay resources from elf file
        ctx(
            rule   = extract_ovl_sections,
            source = app_elf
        )

    ctx.env = cached_env

    ctx.set_group('bundle')

    ctx.custom_pbl_bundle(binaries=binaries,
                   js=ctx.path.ant_glob(['src/pkjs/**/*.js',
                                         'src/pkjs/**/*.json',
                                         'src/common/**/*.js']),
                   js_entry_file='src/pkjs/index.js')

import sys
sys.path.append(os.path.join(sys.prefix,'../sdk-core/pebble/common/tools'))
sys.path.append(os.path.join(sys.prefix,'../sdk-core/pebble/common/waftools'))

import waflib.extras.sdk_paths
import waflib.extras.objcopy as objcopy
import waflib.extras.pebble_sdk_gcc as pebble_sdk_gcc

def custom_generate_bin_file(task_gen,bin_type,elf_file,has_pkjs,has_worker):
    platform_build_node=task_gen.bld.path.get_bld().find_node(task_gen.bld.env.BUILD_DIR)
    packaged_files=[elf_file]
    resources_file=None
    if bin_type!='worker':
        resources_file=platform_build_node.find_or_declare('app_resources.pbpack')
        packaged_files.append(resources_file)
    full_raw_bin_file=platform_build_node.make_node('pebble-{}.full.raw.bin'.format(bin_type))
    raw_bin_file=platform_build_node.make_node('pebble-{}.raw.bin'.format(bin_type))
    bin_file=platform_build_node.make_node('pebble-{}.bin'.format(bin_type))
    task_gen.bld(rule=objcopy.objcopy_bin,source=elf_file,target=full_raw_bin_file)
    def trim_raw_file(task):
        overlay_address=get_overlay_address(task.inputs[0].abspath())
        full_raw    = open( task.inputs[1].abspath() ,'rb' )
        trimmed_raw = open( task.outputs[0].abspath() ,'wb' )
        bytes=full_raw.read(overlay_address)
        trimmed_raw.write(bytes)
    task_gen.bld(rule=trim_raw_file,source=[elf_file, full_raw_bin_file],target=raw_bin_file)
    pebble_sdk_gcc.gen_inject_metadata_rule(task_gen.bld,src_bin_file=raw_bin_file,dst_bin_file=bin_file,elf_file=elf_file,resource_file=resources_file,timestamp=task_gen.bld.env.TIMESTAMP,has_pkjs=has_pkjs,has_worker=has_worker)
    return bin_file

#copied from waflib/extras/process_bundle.py and modified
@feature('custom_pbl_bundle')
def custom_make_pbl_bundle(task_gen):

    bin_files=[]
    bundle_sources=[]
    js_files=getattr(task_gen,'js',[])
    has_pkjs=bool(getattr(task_gen,'js',False))
    if has_pkjs:
        bundle_sources.extend(task_gen.to_nodes(task_gen.js))
    cached_env=task_gen.bld.env
    binaries=task_gen.binaries
    for binary in binaries:
        task_gen.bld.env=task_gen.bld.all_envs[binary['platform']]
        platform_build_node=task_gen.bld.path.find_or_declare(task_gen.bld.env.BUILD_DIR)
        app_elf_file=task_gen.bld.path.get_bld().make_node(binary['app_elf'])
        if app_elf_file is None:
            raise Exception("Must specify elf argument to bundle")
        worker_bin_file=None
        if'worker_elf'in binary:
            worker_elf_file=task_gen.bld.path.get_bld().make_node(binary['worker_elf'])
            app_bin_file=custom_generate_bin_file(task_gen,'app',app_elf_file,has_pkjs,has_worker=True)
            worker_bin_file=custom_generate_bin_file(task_gen,'worker',worker_elf_file,has_pkjs,has_worker=True)
            bundle_sources.append(worker_bin_file)
        else:
            app_bin_file=custom_generate_bin_file(task_gen,'app',app_elf_file,has_pkjs,has_worker=False)
        resources_pack=platform_build_node.make_node('app_resources.pbpack')
        bundle_sources.extend([app_bin_file,resources_pack])
        bin_files.append({'watchapp':app_bin_file.abspath(),'resources':resources_pack.abspath(),'worker_bin':worker_bin_file.abspath()if worker_bin_file else None,'sdk_version':{'major':task_gen.bld.env.SDK_VERSION_MAJOR,'minor':task_gen.bld.env.SDK_VERSION_MINOR},'subfolder':task_gen.bld.env.BUNDLE_BIN_DIR})
    task_gen.bld.env=cached_env
    bundle_output=task_gen.bld.path.get_bld().make_node(task_gen.bld.env.BUNDLE_NAME)
    task=task_gen.create_task('app_bundle',[],bundle_output)
    task.bin_files=bin_files
    task.js_files=js_files
    task.dep_nodes=bundle_sources

from waflib.Configure import conf
@conf
def custom_pbl_bundle(self,*k,**kw):
    kw['features']='js custom_pbl_bundle'
    return self(*k,**kw)