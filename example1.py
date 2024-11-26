from py3dbp import Packer, Bin, Item, Painter
import time
start = time.time()

'''

This example is used to demonstrate the mixed packing of cube and cylinder.

'''

# init packing function
packer = Packer(name = 'Example Packer')
#  init bin
box = Bin('example1', (5.6875, 8, 10.0), 700.0,0,0)
packer.addBin(box)
#  add item
packer.addItem(Item('10kg/7.5kg/Prio1', 'test','cube',(2, 2, 4), 10,1,7.5,True,'red'))
packer.addItem(Item('8kg/7.5kg/Prio1', 'test','cube',(2, 2, 4), 8,1,7.5,True,'blue'))
packer.addItem(Item('8kg/4kg/Prio2', 'test','cube',(2, 2, 4), 8,2,4,True,'gray'))
packer.addItem(Item('3.5kg/2kg/Prio1', 'test','cube',(2, 2, 3), 3.5,1,2,True,'orange'))
packer.addItem(Item('9kg/8kg/Prio1', 'test','cylinder',(3, 2, 4), 9,1,8,True,'lawngreen'))
packer.addItem(Item('8kg/8kg/Prio2', 'test','cylinder',(3, 2, 4), 8,2,8,True,'purple'))
packer.addItem(Item('9kg/8kg/Prio1', 'test','cylinder',(3, 1, 5), 9,1,8,True,'yellow'))
packer.addItem(Item('3kg/2kg/Prio1', 'test','cylinder',(4, 4, 2), 3,1,2,True,'pink'))
packer.addItem(Item('3kg/2.5kg/Prio1', 'test','cylinder',(4, 4, 2), 3,1,2.5,True,'brown'))
packer.addItem(Item('11kg/10kg/Prio1', 'test','cube',(4, 4, 2), 11,1,10,True,'cyan'))
packer.addItem(Item('1.5kg/1.5kg/Prio1', 'test','cylinder',(2, 2, 2), 1.5,1,1.5,True,'olive'))
packer.addItem(Item('2kg/2kg/Prio1', 'test','cylinder',(2, 2, 1), 2,1,2,True,'darkgreen'))
packer.addItem(Item('2.5kg/1kg/Prio1', 'test','cube',(5, 2, 2), 2.5,1,1,True,'orange'))

# calculate packing 
packer.pack(
    bigger_first=True,
    distribute_items=False,
    fix_point=True,
    check_stable=True,
    support_surface_ratio=0.75,
    number_of_decimals=0
)

# print result
b = packer.bins[0]
volume = b.width * b.height * b.depth
print(":::::::::::", b.string())

print("FITTED ITEMS:")
volume_t = 0
volume_f = 0
unfitted_name = ''
for item in b.items:
    print("partno : ",item.partno)
    print("color : ",item.color)
    print("position : ",item.position)
    print("rotation type : ",item.rotation_type)
    print("W*H*D : ",str(item.width) +'*'+ str(item.height) +'*'+ str(item.depth))
    print("volume : ",float(item.width) * float(item.height) * float(item.depth))
    print("weight : ",float(item.weight))
    volume_t += float(item.width) * float(item.height) * float(item.depth)
    print("***************************************************")
print("***************************************************")
print("UNFITTED ITEMS:")
for item in b.unfitted_items:
    print("partno : ",item.partno)
    print("color : ",item.color)
    print("W*H*D : ",str(item.width) +'*'+ str(item.height) +'*'+ str(item.depth))
    print("volume : ",float(item.width) * float(item.height) * float(item.depth))
    print("weight : ",float(item.weight))
    volume_f += float(item.width) * float(item.height) * float(item.depth)
    unfitted_name += '{},'.format(item.partno)
    print("***************************************************")
print("***************************************************")
print('space utilization : {}%'.format(round(volume_t / float(volume) * 100 ,2)))
print('residual volumn : ', float(volume) - volume_t )
print('unpack item : ',unfitted_name)
print('unpack item volumn : ',volume_f)
print("gravity distribution : ",b.gravity)
stop = time.time()
print('used time : ',stop - start)

# draw results
painter = Painter(b)
fig = painter.plotBoxAndItems(
    title=b.partno,
    alpha=0.2,
    write_name=True,
    fontsize=10
)
