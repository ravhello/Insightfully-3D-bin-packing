from py3dbp import Packer, Bin, Item, Painter
import time

start = time.time()

'''
If you have multiple boxes, you can change distribute_items to achieve different packaging purposes.
1. distribute_items=True , put the items into the box in order, if the box is full, the remaining items will continue to be loaded into the next box until all the boxes are full  or all the items are packed.
2. distribute_items=False, compare the packaging of all boxes, that is to say, each box packs all items, not the remaining items.
'''

# Initialize the packing function
packer = Packer(name='Example Packer')

# Initialize bins
box = Bin('example7-Bin1', (5, 5, 5), 100, 0, 0)
box2 = Bin('example7-Bin2', (3, 3, 5), 100, 0, 0)

# Add bins to the packer
packer.addBin(box)
packer.addBin(box2)

# Add items to the packer
items = [
    ('Box-1', (5, 4, 1), 'yellow'),
    ('Box-2', (1, 2, 4), 'blue'),
    ('Box-3', (1, 2, 3), 'orange'),
    ('Box-4', (1, 2, 2), 'grey'),
    ('Box-5', (1, 2, 3), 'green'),
    ('Box-6', (1, 2, 4), 'red'),
    ('Box-7', (1, 2, 2), 'pink'),
    ('Box-8', (1, 2, 3), 'olive'),
    ('Box-9', (1, 2, 4), 'olive'),
    ('Box-10', (1, 2, 3), 'pink'),
    ('Box-11', (1, 2, 2), 'olive'),
    ('Box-12', (5, 4, 1), 'pink'),
    ('Box-13', (1, 1, 4), 'olive'),
    ('Box-14', (1, 2, 1), 'pink'),
    ('Box-15', (1, 2, 1), 'red'),
    ('Box-16', (1, 1, 4), 'blue'),
    ('Box-17', (1, 1, 4), 'olive'),
    ('Box-18', (5, 4, 2), 'brown'),
]

for partno, dimensions, color in items:
    packer.addItem(Item(
        partno=partno,
        name=partno,
        typeof='cube',
        WHD=dimensions,
        weight=1,
        level=1,
        loadbear=100,
        updown=True,
        color=color
    ))

# Calculate packing
packer.pack(
    bigger_first=True,
    distribute_items=False,  # Change this to True to compare packing across bins
    fix_point=True,
    check_stable=True,
    support_surface_ratio=0.75,
    number_of_decimals=0
)

# Print and visualize results
for idx, b in enumerate(packer.bins):
    print("***************************************************")
    print(f"** {b.string()} **")
    print("***************************************************")
    print("FITTED ITEMS:")
    print("***************************************************")

    volume = b.width * b.height * b.depth
    volume_t = 0

    if not b.items:
        print(f"Bin {b.partno} is empty. Skipping plot.")
        continue

    for item in b.items:
        item_volume = float(item.width) * float(item.height) * float(item.depth)
        volume_t += item_volume
        print(f"partno : {item.partno}")
        print(f"color : {item.color}")
        print(f"position : {item.position}")
        print(f"rotation type : {item.rotation_type}")
        print(f"W*H*D : {item.width} * {item.height} * {item.depth}")
        print(f"volume : {item_volume}")
        print(f"weight : {item.weight}")
        print("***************************************************")
    
    print(f"space utilization : {round(volume_t / float(volume) * 100, 2)}%")
    print(f"residual volume : {float(volume) - volume_t}")
    print(f"gravity distribution : {b.gravity}")
    print("***************************************************")

    # Generate and show plot for the current bin
    painter = Painter(b)
    fig = painter.plotBoxAndItems(
        title=b.partno,
        alpha=0.8,
        write_name=False,
        fontsize=10
    )