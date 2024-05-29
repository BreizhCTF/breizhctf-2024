import pefile

# A Linux based function, extracting resource from .rsrc section but obviously the easiest solution is to debug the process or simply open the .exe in an archive manager and get the string resource directly

def find_resource_offset(pe, resource_id):
    resource_directory = None
    for section in pe.sections:
        if section.Name.decode().strip('\x00') == '.rsrc':
            resource_directory = section
            break
    if resource_directory is None:
        raise ValueError("Resource directory (.rsrc) not found")

    resource_table = pe.parse_resources_directory(resource_directory.VirtualAddress)

    for resource_type in resource_table.entries:
        if hasattr(resource_type, 'directory'):
            for resource_name in resource_type.directory.entries:
                if hasattr(resource_name, 'directory'):
                    for resource_id_entry in resource_name.directory.entries:
                        if resource_id_entry.id == 1036:
                            offset = resource_id_entry.data.struct.get_file_offset()
                            return offset
    return None

pe_file_path = '../dist/AllIsIn.exe'
pe = pefile.PE(pe_file_path)
resource_id = 101
rsrc_offset = find_resource_offset(pe, resource_id)
pe_file = open(pe_file_path, 'rb')
pe_file.seek(rsrc_offset)
str_off = pe.get_offset_from_rva(int.from_bytes(pe_file.read(4), 'little')+10)
pe_file.seek(str_off)
str_len = int.from_bytes(pe_file.read(2), 'little')
pe_file.seek(str_off+2)
flag = ''
for i in range(str_len):
    flag += chr(pe_file.read(2)[0]+5)
print('Flag:', flag)
pe_file.close()
