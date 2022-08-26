from collections import defaultdict

from src.Core.Galaxy import Galaxy

EXPLORETIMES = 1  # 设置单次探险舰队数目
EXPLORETARGET = []  # 设置探险目标 格式如[[1,1,1],[1,1,2]]
EXPLORELEVEL = 99  # 选择探险舰队

ATTACKTIMES = 1  # 设置单次舰队探险数目
ATTACKTARGET = []  # 设置攻击目标 格式如上 建议攻击五个以上 探险一个足够
ATTACKLEVEL = 20  # 选择攻击舰队

fleet = {
    20: defaultdict(int, {
        'ds': 2,
        'bs': 0,
        'de': 0,
        'cargo': 0
    }),
    25: defaultdict(int, {'ds': 10}),
    10: defaultdict(int, {
        'bs': 15,
        'cargo': 15
    }),
    12: defaultdict(int, {
        'bs': 40,
        'cargo': 30
    }),
    16: defaultdict(int, {
        'bs': 260,
        'cargo': 35
    }),
    88: defaultdict(int, {
        'cargo': 50,
        'bs': 50,
        'satellite': 200
    }),
    99: defaultdict(int, {'satellite': 2000})
}

attackTargetList = []
exploretargetList = []


def target2lst(TARGET, Lst):
    for i in TARGET:
        Lst.append(dict(zip(['galaxy', 'system', 'planet'], i)))


if __name__ == '__main__':
    target2lst(ATTACKTARGET, attackTargetList)
    target2lst(EXPLORETARGET, exploretargetList)
    task = defaultdict(int)
    task['attack'] = 1  # 1 启用攻击任务 0 关闭攻击任务
    task['explore'] = 1  # 1 启用探测任务 0 关闭探测任务
    task['escape'] = 1  # 1 启用逃逸任务 0 关闭逃逸任务
    G = Galaxy('user', 'pass', 'g10')  # 依次为 用户名 密码 服务器
    G.getTasks(attackTargetList, (ATTACKLEVEL, ATTACKTIMES), exploretargetList, (EXPLORELEVEL, EXPLORETIMES), task,
               fleet)
    G.run()
