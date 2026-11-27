"""Animate the three maps in the representative-row example."""

import math
from fractions import Fraction as F
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
W,H = 704,835
BG,PANEL,EDGE = "#101b32","#162640","#3c5778"
TEXT,MUTED = "#f7faff","#becbe0"
MINT,AMBER,BLUE = "#6aead7","#ffd086","#a9bdfb"
COLORS = (AMBER,MINT,BLUE)
MAPS = ((1,2,1),(2,1,1),(1,1,1))


def label(draw, xy, message, size, color=TEXT, anchor="lt"):
    draw.text(xy,message,font=ImageFont.load_default(size=size),fill=color,anchor=anchor)


def prism(draw, x, y, angle, name, active):
    dx = 15 * math.cos(angle)
    top = [(x-29,y-25),(x+dx,y-42),(x+29,y-25),(x-dx,y-8)]
    left = [top[0],top[3],(x-dx,y+16),(x-29,y)]
    right = [top[3],top[2],(x+29,y),(x-dx,y+16)]
    colors = ("#44627b","#29445c","#527990") if active else ("#334767","#263a56","#4c5f7f")
    for poly,color in zip((left,right,top),colors):
        draw.polygon(poly,fill=color,outline="#14233a")
    label(draw,(x,y-24),name,28,TEXT,"mm")


def graph(draw, angle, index):
    mapping = MAPS[index]
    offset = 14 * math.sin(angle)
    depth = 7 * math.cos(angle)
    starts = [(161+offset,330+depth),(352+offset,330),(543+offset,330-depth)]
    ends = [(161-offset,502-depth),(352-offset,502),(543-offset,502+depth)]
    for j,(sx,sy) in enumerate(starts):
        tx,ty=ends[mapping[j]-1]
        bend=(j-1)*11
        points=[(sx,sy+10)]
        for i in range(1,23):
            t=i/22
            points.append((sx+t*(tx-sx)+bend*math.sin(math.pi*t),sy+10+t*(ty-sy-43)))
        draw.line(points,fill=COLORS[j],width=5)
    for j,(x,y) in enumerate(starts):
        prism(draw,x,y,angle,str(j+1),True)
    for j,(x,y) in enumerate(ends):
        prism(draw,x,y,angle,str(j+1),j+1 in mapping)


def frame(angle, index):
    weight = (F(0),F(0),F(1,4))[index]
    left,right=1+weight,1-weight
    selected=("e = (1, 2, 1)","f = (2, 1, 1)","g = (1, 1, 1)")[index]
    image=Image.new("RGB",(W,H),BG)
    d=ImageDraw.Draw(image)
    label(d,(36,36),"FINITE GRAND COUPLINGS",24,MINT)
    label(d,(34,83),"From maps to fibers",55)
    label(d,(36,156),"Three trajectories share each draw.",29,MUTED)
    d.rounded_rectangle((32,210,672,558),21,fill=PANEL,outline=EDGE,width=2)
    label(d,(55,236),"SELECTED MAP",22,MUTED)
    label(d,(648,236),selected,29,TEXT,"rt")
    graph(d,angle,index)
    d.rounded_rectangle((32,580,672,802),21,fill=PANEL,outline=EDGE,width=2)
    label(d,(55,600),"Column sums for e's fibers",30)
    label(d,(55,655),f"{{1,3}} gives {left}",31,AMBER)
    label(d,(648,655),f"{{2}} gives {right}",31,MINT,"rt")
    notes=(("e first merges states 1 and 3.","The two compressed columns balance."),
           ("f first merges states 2 and 3.","The same compressed columns balance."),
           ("Give the constant map probability 1/4.","All seven affine tests exclude an obstruction."))
    label(d,(55,718),notes[index][0],26,MUTED)
    label(d,(55,753),notes[index][1],25,MUTED)
    return image.convert("P",palette=Image.Palette.ADAPTIVE,colors=64)


def main():
    total=72
    frames=[frame(2*math.pi*i/total,i//24) for i in range(total)]
    frames[0].save(HERE/"grand-coupling.gif",save_all=True,append_images=frames[1:],
                   loop=0,duration=180,optimize=True)
    with ZipFile(HERE/"grand-coupling-explorer.zip","w") as archive:
        for name in ("README.md","index.html"):
            info=ZipInfo(name,(1980,1,1,0,0,0))
            info.create_system=3
            info.external_attr=0o100644<<16
            archive.writestr(info,(HERE/name).read_bytes(),ZIP_DEFLATED,compresslevel=9)


if __name__=="__main__":
    main()
