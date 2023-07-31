# # coding=utf-8

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator

plt.rcParams['font.sans-serif'] = ['Arial']  # 如果要显示中文字体,则在此处设为：SimHei
plt.rcParams['axes.unicode_minus'] = False  # 显示负号

x = np.array([5, 10, 20, 40, 80])
share = np.array([63.002259, 126.1997, 243.66857, 498.574039, 983.14892])
reenc = np.array([194.25862, 197.671269, 198.93531, 194.550669, 197.87574])
cipher_aggregate = np.array([0.10438, 0.234209, 0.488019, 1.08131, 2.14207])
# label在图示(legend)中显示。若为数学公式,则最好在字符串前后添加"$"符号
# color：b:blue、g:green、r:red、c:cyan、m:magenta、y:yellow、k:black、w:white、、、
# 线型：-  --   -.  :    ,
# marker：.  ,   o   v    <    *    +    1
# x_major_locator=MultipleLocator(100)
fig = plt.figure(figsize=(10, 5))
plt.grid(linestyle="--")  # 设置背景网格线为虚线
plt.xticks(x, fontsize=12, fontweight='bold')  # 默认字体大小为10
plt.yticks(fontsize=12, fontweight='bold')
plt.xlabel("Number of proxies", fontsize=13, fontweight='bold')
plt.ylabel("Time cost(ms)", fontsize=13, fontweight='bold')

ax = fig.add_subplot()
ax.spines['top'].set_visible(False)  # 去掉上边框
ax.spines['right'].set_visible(False)  # 去掉右边框
ax.plot(x, share, label='RKShare', color='blue', marker='s', linewidth=1.5)
ax.plot(x, reenc, label='PartReEnc', color='green', marker='s', linewidth=1.5)
ax.set_ylabel("Time cost(ms)")
ax.set_ylim(0, 1000)
ax.legend(loc='upper left')

ax2 = ax.twinx()
ax2.plot(x, cipher_aggregate, label='Comb', color='red', marker='s', linewidth=1.5)
ax2.set_ylabel("Time cost(ms)", fontsize=13, fontweight='bold')
ax2.set_yticklabels(cipher_aggregate, fontdict={'fontsize':12, 'fontweight':'bold'})
ax2.set_ylim(0, 2.25)
ax2.legend(loc='upper right')

ax.set_xlabel("Number of proxies")
plt.show()
# plt.figure(figsize=(10, 5))
# plt.grid(linestyle="--")  # 设置背景网格线为虚线

# ax.xaxis.set_major_locator(x_major_locator)
# ax2 = ax.twinx()


# ax.plot(x, share, marker='s', label="RKShare", color="blue", linewidth=1.5)
# ax.plot(x, reenc, marker='s', label="PartReEnc", color="green", linewidth=1.5)
# ax2.plot(x, cipher_aggregate, marker='s', label="Comb", color="red", linewidth=1.5)

# # group_labels = ['5', '10', '20', '40', '80']  # x轴刻度的标识
# plt.xticks(x, fontsize=12, fontweight='bold')  # 默认字体大小为10
# plt.yticks(fontsize=12, fontweight='bold')
# # plt.title("example", fontsize=12, fontweight='bold')  # 默认字体大小为12
# plt.xlabel("Number of proxies", fontsize=13, fontweight='bold')
# plt.ylabel("Time cost(ms)", fontsize=13, fontweight='bold')
# plt.xlim(0, 90)  # 设置x轴的范围
# ax2.ylim(0, 2.25)

# # # plt.legend()          #显示各曲线的图例
# # plt.legend(loc=0, numpoints=1)
# # leg = plt.gca().get_legend()
# # ltext = leg.get_texts()
# # plt.setp(ltext, fontsize=12, fontweight='bold')  # 设置图例字体的大小和粗细

# # plt.savefig('fig1.svg', format='svg')  # 建议保存为svg格式,再用inkscape转为矢量图emf后插入word中
# # plt.savefig('fig1.eps',dpi=1200,format='eps')
# plt.savefig('fig2.svg', format='svg')  # 建议保存为svg格式,再用inkscape转为矢量图emf后插入word中
# plt.savefig('fig2.eps',dpi=1200,format='eps')
# # plt.savefig('fig3.svg', format='svg')  # 建议保存为svg格式,再用inkscape转为矢量图emf后插入word中
# # plt.savefig('fig3.eps',dpi=1200,format='eps')
# plt.show()

# # coding=utf-8

# # import numpy as np
# # import matplotlib.pyplot as plt

# # plt.rcParams['font.sans-serif'] = ['Arial']  # 如果要显示中文字体,则在此处设为：SimHei
# # plt.rcParams['axes.unicode_minus'] = False  # 显示负号

# # x = np.array([5, 10, 20, 40, 80])
# # arithm_share = np.array([35.745519, 65.351, 126.216589, 243.06483, 491.71047])
# # shamir_share = np.array([79.390048, 197.82987, 382.0771, 760.641159, 1482.14892])
# # ourNetwork = np.array([2.0205495, 2.6509762, 3.1876223, 4.380781, 6.004548, 9.9298])

# # # label在图示(legend)中显示。若为数学公式,则最好在字符串前后添加"$"符号
# # # color：b:blue、g:green、r:red、c:cyan、m:magenta、y:yellow、k:black、w:white、、、
# # # 线型：-  --   -.  :    ,
# # # marker：.  ,   o   v    <    *    +    1
# # plt.figure(figsize=(10, 5))
# # plt.grid(linestyle="--")  # 设置背景网格线为虚线
# # ax = plt.gca()
# # ax.spines['top'].set_visible(False)  # 去掉上边框
# # ax.spines['right'].set_visible(False)  # 去掉右边框


# # plt.plot(x, arithm_share, marker='s', label="Additive Secret Sharing", color="blue", linewidth=1.5)
# # plt.plot(x, shamir_share, marker='s', color="green", label="Shamir Secret Sharing", linewidth=1.5)

# # # group_labels = ['Top 0-5%', 'Top 5-10%', 'Top 10-20%', 'Top 20-50%', 'Top 50-70%', ' Top 70-100%']  # x轴刻度的标识
# # plt.xticks(x, fontsize=12, fontweight='bold')  # 默认字体大小为10
# # plt.yticks(fontsize=12, fontweight='bold')
# # # plt.title("example", fontsize=12, fontweight='bold')  # 默认字体大小为12
# # plt.xlabel("Number of proxies", fontsize=13, fontweight='bold')
# # plt.ylabel("Time cost(ms)", fontsize=13, fontweight='bold')
# # plt.xlim(0, 90)  # 设置x轴的范围
# # plt.ylim(0, 1600)

# # # plt.legend()          #显示各曲线的图例
# # plt.legend(loc=0, numpoints=1)
# # leg = plt.gca().get_legend()
# # ltext = leg.get_texts()
# # plt.setp(ltext, fontsize=12, fontweight='bold')  # 设置图例字体的大小和粗细

# # plt.savefig('fig1.svg', format='svg')  # 建议保存为svg格式,再用inkscape转为矢量图emf后插入word中
# # plt.savefig('fig1.eps',dpi=1200,format='eps')
# # plt.show()
