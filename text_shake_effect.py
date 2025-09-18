from moviepy.editor import *


#A function used to shake the text
#The text gets increasingly larger each second
def text_shake_effect(start_time,text,dur,shake_dur = 0.075,color=[255,255,255],font_size=200,stroke_width = 1.075,stroke_color="black",font=""):

    captions = []

    real_font_size = font_size
    shake_frames = 25

    extra_font_size = (real_font_size*1)/shake_frames
    extra_dur = shake_dur/shake_frames

    for i in range(shake_frames-1):

        sample_caption = TextClip(txt=text,fontsize=(i+1)*extra_font_size,stroke_color=stroke_color,stroke_width=stroke_width,color=color,font=font).set_position("center").set_start(start_time+extra_dur*i).set_duration(extra_dur)

        captions.append(sample_caption)
    

    last_caption = TextClip(txt=text,fontsize=real_font_size,stroke_color=stroke_color,stroke_width=stroke_width,color=color,font=font).set_position("center").set_duration(dur-shake_dur).set_start(start_time+shake_dur)

    captions.append(last_caption)

    return captions
