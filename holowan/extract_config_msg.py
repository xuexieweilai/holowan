import re


def extract_msg():
    open_file_pathAndname = '/Users/lixingda/Downloads/net.config'
    write_file_pathAndname = '/Users/lixingda/Downloads/new_config.txt'
    f = open(open_file_pathAndname, 'r')
    n = 0
    holowan_list = []
    content = f.read()
    first_words = re.match(r'.+: random update config', content).group()
    big_group = content.split(first_words)
    new_big_group = [x.strip() for x in big_group if x.strip() != '']
    for small_group in new_big_group:
        n += 1
        jitter_dict = {'id': n,
                       'uploadDict':{},
                       'downloadDict': {}
                       }
        new_small_group = small_group.split('\n')
        for ss in new_small_group:
            reason_one = re.match(r'^\[I\]Update\s+bandwidth\s+config\s+to\s+jitter\s+with\s+range\s+\[(\d+),\s*(\d+)\](\w+),\s+period\s+(\d+)s,\s+wave:\s+(\w+)', ss)
            reason_two = re.match(r'^\[I\]Update\s+propagation\s+config\s+to\s+fixed\s+(\d+)\s+ms', ss)
            reason_three = re.match(r'^\[I\]Update\s+loss\s+config\s+to\s+fixed\s+(\d*\.?\d+?)%', ss)
            reason_four = re.match(r'^\[I\]Update\s+propagation\s+config\s+to\s+uniform\s+with\s+range\s+\[(\d+),\s*(\d+)\]ms,\s+reorder\s+(\d+)', ss)
            reason_five = re.match(r'^\[I\]Update\s+bandwidth\s+config\s+to\s+fixed\s+(\d+)\s+(\w+)', ss)
            if reason_one:
                '''带宽jitter'''
                bandwith_min_upload = reason_one.group(1)
                bandwith_max_upload = reason_one.group(2)
                bandwith_t_upload = reason_one.group(3)     # 单位
                bandwith_cycle_upload = reason_one.group(4)    # 周期
                bandwith_type_id_upload = reason_one.group(5) # 波形曲线id
                '''判断波形曲线'''
                if bandwith_type_id_upload.lower() == 'sine':
                    jitter_dict['uploadDict']['bandwith_type_id_upload'] = '1'
                elif bandwith_type_id_upload.lower() == 'sawtooth':
                    jitter_dict['uploadDict']['bandwith_type_id_upload'] = '5'
                elif bandwith_type_id_upload.lower() == 'polyline_wave':
                    jitter_dict['uploadDict']['bandwith_type_id_upload'] = '2'
                '''判断传入的单位：  1：bps, 2: kbps, 3: mbps'''
                if bandwith_t_upload.lower() == 'bps':
                    jitter_dict['uploadDict']['bandwith_t_upload'] = 1
                elif bandwith_t_upload.lower() == 'kbps':
                    jitter_dict['uploadDict']['bandwith_t_upload'] = 2
                elif bandwith_t_upload.lower() == 'mbps':
                    jitter_dict['uploadDict']['bandwith_t_upload'] = 3
                jitter_dict['uploadDict']['bandwith_min_upload'] = bandwith_min_upload
                jitter_dict['uploadDict']['bandwith_max_upload'] = bandwith_max_upload
                jitter_dict['uploadDict']['bandwith_cycle_upload'] = bandwith_cycle_upload
                jitter_dict['uploadDict']['bandwith_type_upload'] = 2        # bandwith_type_upload 限制带宽类型[1. 正常模式， 2. 抖动模式]
                continue

            if reason_two:
                '''Delay-Constant'''
                jitter_dict['uploadDict']['delay_type_upload'] = '1'
                jitter_dict['uploadDict']['delay_const_upload'] = reason_two.group(1)
                continue

            if reason_three:
                '''丢包类型： 1： Random'''
                loss_r_upload = reason_three.group(1)
                jitter_dict['uploadDict']['loss_type_upload'] = '1'
                jitter_dict['uploadDict']['loss_r_upload'] = loss_r_upload
                continue
            if reason_four:
                '''Delay-uniform'''
                delay_dmi_upload = reason_four.group(1)
                delay_dma_upload = reason_four.group(2)
                delay_reo_upload = reason_four.group(3)     # 是否乱序， 0 不  1 乱
                jitter_dict['uploadDict']['delay_type_upload'] = '2'
                jitter_dict['uploadDict']['delay_dmi_upload'] = delay_dmi_upload
                jitter_dict['uploadDict']['delay_dma_upload'] = delay_dma_upload
                jitter_dict['uploadDict']['delay_reo_upload'] = int(delay_reo_upload)
                continue
              # TODO Delay-Normal还没有写

            if reason_five:
                '''带宽fixed'''
                bandwith_value_upload = reason_five.group(1)
                bandwith_t_upload = reason_five.group(2)    # 带宽单位
                if bandwith_t_upload.lower() == 'bps':
                    jitter_dict['uploadDict']['bandwith_t_upload'] = 1
                elif bandwith_t_upload.lower() == 'kbps':
                    jitter_dict['uploadDict']['bandwith_t_upload'] = 2
                elif bandwith_t_upload.lower() == 'mbps':
                    jitter_dict['uploadDict']['bandwith_t_upload'] = 3
                jitter_dict['uploadDict']['bandwith_type_upload'] = 1    # bandwith_type_upload 限制带宽类型[1. 正常模式， 2. 抖动模式]
                jitter_dict['uploadDict']['bandwith_value_upload'] = bandwith_value_upload    # 值
                continue
        holowan_list.append(str(jitter_dict) + ','+'\n')
    with open(write_file_pathAndname, 'w+') as new_write_con:
        new_write_con.write('[')
        new_write_con.writelines(holowan_list)
        new_write_con.write(']')
    f.close()



if __name__ == '__main__':
    extract_msg()