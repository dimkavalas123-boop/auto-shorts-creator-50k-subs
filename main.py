import os,random,moviepy,math
from moviepy.editor import VideoFileClip,AudioFileClip,CompositeAudioClip,CompositeVideoClip,afx,concatenate_audioclips,concatenate_videoclips,ImageClip
from pydub import AudioSegment, silence
from text_shake_effect import text_shake_effect

from deepgram import Deepgram


DEEPGRAM_API_KEY = "your_api_key_here"

def transcribe(audio_file_path):
    # Initializes the Deepgram SDK
    deepgram = Deepgram(DEEPGRAM_API_KEY)
    # Open the audio file

    with open(audio_file_path, 'rb') as audio:
        # ...or replace mimetype as appropriate
        source = {'buffer': audio, 'mimetype': 'audio/wav'}
        response = deepgram.transcription.sync_prerecorded(source, {'punctuate': True})
        
        return response
    

    
def delete_silence_from_clip(min_silence=500): #350
    # Load the audio from the video file
    audio = AudioSegment.from_file("speech.wav")

    min_silence_length = min_silence  # Minimum silence duration in milliseconds

    # Detect silence regions
    silence_regions = silence.detect_silence(audio, min_silence_len=min_silence_length, silence_thresh=-200)

    start = 0
    region_end = 0
    non_silence_parts = []

    for region_start, region_end in silence_regions:
        if region_end > len(audio) or region_start > len(audio):
            break

        non_silence_parts.append([start, min(len(audio), region_start)])

        start = region_end

    non_silence_parts.append([region_end, len(audio)])

    # Extract non-silence segments and concatenate them
    result_audio = AudioSegment.empty()
    for start, end in non_silence_parts:
        result_audio += audio[start:end]

    # Export the result to the same file
    result_audio.export("speech.wav", format="wav")


#Makes the video be in short form
def return_short_version(video_file):
    # Define the desired width and height (9:16 aspect ratio)
    target_width = 1080  # You can adjust this width as needed
    target_height = 1920  # This height corresponds to a 9:16 aspect ratio

    video_file = video_file.resize(height=target_height)

    # Crop the video to the desired size
    x_center = video_file.w / 2
    x1 = x_center - (target_width / 2)
    x2 = x_center + (target_width / 2)
    
    video_file = video_file.crop(x1=x1, x2=x2, y1=0, y2=target_height)

    return video_file




#Selects and creates background footage 
def select_background_footage(dur,footage,last_clip_name):

    video_file = random.choice( os.listdir(footage) )
    video_sample = VideoFileClip(f"{footage}/{video_file}")

    start = random.randint(int(video_sample.duration*0.25),int(video_sample.duration*0.75) )
    video_sample_clip = video_sample.subclip( start,start+dur )

    #It reapets the proccess until it has not chosen the same background clip
    while start + dur > video_sample.duration or video_file == last_clip_name:
        video_file = random.choice( os.listdir(footage) )
        video_sample = VideoFileClip(f"{footage}/{video_file}")

        start = random.randint(int(video_sample.duration*0.25),int(video_sample.duration*0.75) )
        video_sample_clip = video_sample.subclip( start,start+dur )


    return return_short_version(video_sample_clip),video_file


#Selects and creates background music
def get_music(footage):
    music_path = random.choice(os.listdir(footage))
    music = AudioFileClip(f"{footage}/{music_path}")

    return music



def get_sound_file(path):

    vid = AudioFileClip(path)

    vid.write_audiofile("speech.wav")


#Adds sound effects to the result video evenly
def add_rnd_sfxs(video_result):
    sample_folder = "SampleSfxs"

    audio_clips = []

    #Fills the audio_clips with each sfx starting at the appropriate time to be evenly heard throught the whole video
    for indx,i in enumerate(os.listdir(sample_folder)):
        sample_path = f"{sample_folder}/{i}"

        sample_audio_clip = VideoFileClip( sample_path ).set_start((indx+1)*(video_result.duration/(1+len(os.listdir(sample_folder)) ) )).audio

        audio_clips.append(sample_audio_clip)


    audio_clips =CompositeAudioClip(audio_clips)
    audio_clips = audio_clips.subclip(0,video_result.duration)
    video_result.audio = CompositeAudioClip([video_result.audio,audio_clips])

    return video_result


def create_video(footage,music_footage,font,name,path_video,
                fps = 50,
                start_comment_path = "comment.png",
                woosh_sfx_path = "woosh_heavy_sfx.mp4",
                word_to_caption = [2,1],
                transition_timestamp = 2.7,
                late_transition=1.7,
                sample_color = "#7fc2e3",
                result_fontsize=110,
                font_margin=5,
                low_edit_start_time=2.7,
                music_vol=0.65,
                red_arrow_dur=1.5,
                add_rnd_sfx=True,
                all_vol=1.35,
                comment_movement=True):

    #path_video
    "The path of the video with the recording that has the audio for the video"

    #fps
    "Frames Per Second, for the video created"

    #start_comment_path
    "The path to the comment that will be displayed at the start of the video, if you do not wish to include a comment, set the variable to None"

    #high_editting
    """The program has 2 states determined from the high_edititng var.
    If it is set to True, the transitions, cuts etc are more frequent and the color of the captions changes randomly.
    If it is set to False, there are less cuts and trasnisitions and the color is set to the one of your choice
    At the start of the video, high editting is always set to False, after a period of time the high editting var is set to True"""

    #woosh_sfx_path
    "The woosh_sfx_path is the path to a sound effect that is going to be played every time the background video changes"

    #words_to_caption
    """The words_to_caption determines how many words are going to be displayed in every subtitle. 
    If the editting is "high", meaing there are lots of cuts and tranistions, the word_per_caption var is set to the second val of word_to_caption.
    If it isn't, it is the first val"""

    #transition_timestamp
    "The transition_timestamp determines the period of time it takes to change the video of the background. This var is for when high_editting = False"

    #late_transition
    """The late_trasnition determines the period of time it takes to change the video of the background.
    The only difference is that this var is for every clip after the first one (I prefer the firsr clip being longer in duration)"""

    #result_fontsize
    "The base font used by the algorithm. (The font size changes a bit when the mode is high editting )"

    #font_margin
    "The font used when in high editting is font_size += -+ font_margin (The size changes a little in each caption randomly)"

    #low_edit_start_time
    "The time in the start of the video when high_editting is not activated. When the time has passed, from the next clip high editting will be activated"

    #music_vol
    "How loud the background music will be"

    #red_arrow_dur
    "How long the red arrow pointing at the subscribe button will be displayed, if you wish for the arrow to not be displayed, set variable to None"

    #add_rnd_sfxs
    """If set to True, the sound effects from the SampleSfxs folder will be played evenly displayed throught the video to keep watch time high.
    If set to False, none of these sound effects will be used"""

    #comment_movement
    "If set to True, the start comment will follow the text_random_movement.If not, it will be stationary"

    #all_vol
    "How loud the audio of the video is going to be"

    target_width = 1080  



    #Creates a .wav file with the audio from the video recording named "speech.wav"
    get_sound_file(path_video)
    # Deletes the silence from the "speech.wav" file
    delete_silence_from_clip()

    #Transcribes the "speech.wav" file
    transcribed_text = transcribe("speech.wav")

    transcript = transcribed_text["results"]["channels"][0]["alternatives"][0]["transcript"]

    tries = -1

    #A video with just silence, it will be used later in code
    silence = VideoFileClip("silence.mp4").audio

    while True:
        tries += 1

        high_editting = False

        words_per_caption = word_to_caption[ int(high_editting)]
        
        captions = []
        background_footage = []

        sample_start = 0
        text_presenting = ""
        word_num = 0
        sample_start = 0
        rewrite = True

        footage_duration = 0

        sample_woosh = AudioFileClip(woosh_sfx_path).set_start(0)
        sample_woosh = sample_woosh.fx( afx.volumex, 0.3)

        woosh_sfxs = [sample_woosh]
        last_clip_name = ""
        
        #Creates each caption
        for i,sample_word in enumerate(transcript.split(" ")):
            
            sample_word = sample_word.lower()

            #Gets the transcripiton data for the word reviewing right now
            word_section = transcribed_text["results"]["channels"][0]["alternatives"][0]["words"][i]
            text_presenting += f"{sample_word} "

            word_num += 1
            #If the text is too long it changes to a new line
            if words_per_caption > 3 and word_num == words_per_caption//2:
                text_presenting += "\n"

            if rewrite:
                sample_start = word_section["start"]
                rewrite = False

            #Determines if the sentence has ended, to also close the caption
            end_sentence = [i in sample_word for i in [".","?",",","!"]]            

            #If the caption has reached word limit or the sentence has ended, it stops adding word to the caption
            if word_num >= words_per_caption or True in end_sentence:

                word_num = 0
                words_per_caption = word_to_caption[ int(high_editting)]
                
                
                result_txt = "".join([i.upper() for i in text_presenting])

                print(f"Sentence: {result_txt} and {i}/{len(transcript.split(' '))}")

                #Choses if the caption is going to be lower, captialized or all upper case in random
                style_choice = random.choice(["lower", "capitalize", "upper"])
                if style_choice == "lower": result_txt = text_presenting.lower()
                elif style_choice == "capitalize": result_txt = text_presenting.capitalize()
                else: result_txt = text_presenting.upper()

                #Determines the color used, if it is high editting, the algorithm chooses a color randomly
                result_color =  [sample_color,random.choice( ["white","pink","white","yellow","white"] )] [int(high_editting)] 
                
                #The font size used, if it is in high editting, there is a chance that the font_size changes
                result_fontsize += [0,random.choice([0,font_margin,-font_margin])][int(high_editting)] 

                #Determines how long the caption should be displayd for
                sample_duration = word_section["end"] - sample_start

                #Adds the shake text effect to the caption that was just created
                sample_caption = text_shake_effect(sample_start,result_txt,sample_duration,font_size = result_fontsize,color=result_color,font=font)

                #Adding Background Footage
                if footage_duration > transition_timestamp:
                
                    woosh_sfxs.append( sample_woosh )

                    #Creates a random bg for the video
                    sample_footage,last_clip_name = select_background_footage(footage_duration,footage,last_clip_name)

                    sample_footage = moviepy.video.fx.all.fadeout(sample_footage,0.25,(255,255,255))
                    
                    sample_footage.audio = None

                    #Creates a silence as long as the subclip
                    sample_silence = silence.subclip(0,sample_footage.duration - sample_woosh.duration)

                    #Mutes the audio from the bg video and adding the woosh effect
                    sample_footage.audio = concatenate_audioclips((sample_woosh,sample_silence))
    

                    background_footage.append(sample_footage)
                    footage_duration = 0

                    #When adding new background footage, it detects whether enough time has passed to enter high editting mode
                    if sample_start + sample_duration > low_edit_start_time:
                        transition_timestamp = late_transition
                        high_editting = True
                    
                rewrite = True
                text_presenting = ""

                footage_duration += sample_duration
                captions += sample_caption
        

        print("Adding Details...")

        speech = AudioFileClip("speech.wav")

        #Generates the background music
        music = get_music(music_footage).subclip(0,speech.duration)    
        music = music.fx( afx.volumex, music_vol)    

        #Merges the AI voice with the bg music
        should_audio = CompositeAudioClip((music,speech))

        r_background_footage = concatenate_videoclips(background_footage)
        sample_footage,_ = select_background_footage(-r_background_footage.duration+should_audio.duration,footage,last_clip_name)
        
        sample_silence = silence.subclip(0,sample_footage.duration - sample_woosh.duration)
        sample_footage.audio = concatenate_audioclips((sample_woosh,sample_silence))
        
        background_footage.append(sample_footage)
        r_background_footage = concatenate_videoclips(background_footage)
        r_background_footage = r_background_footage.set_start(0)

        #Creates the background footage as a seperate video, this is to lower the waiting time
        r_background_footage.write_videofile("bg_footage_alone.mp4")
        background_footage_result = VideoFileClip("bg_footage_alone.mp4")

        result_captions = [background_footage_result] + captions

        video_result = CompositeVideoClip(result_captions)
        video_result.audio = CompositeAudioClip( (should_audio,video_result.audio) )


        if start_comment_path != None:
            comment_start = ImageClip(start_comment_path).set_duration(5).set_start(0)
            
            multiplier = (target_width)/(comment_start.size[0])
            comment_start = comment_start.resize(width=700)
            comment_start = comment_start.resize(height=multiplier * comment_start.size[1])

            comment_start = comment_start.set_position(( (target_width/2)-(comment_start.size[0]/2) ,200))

            #Determines wether there will be an animation or not
            if comment_movement:
                comment_start = text_random_movement(comment_start)

            video_result = CompositeVideoClip([video_result] + comment_start)


        if red_arrow_dur != None:
            start_time = video_result.duration - red_arrow_dur
            red_arrow = ImageClip("red_arrow.png").set_start(start_time).set_duration(red_arrow_dur)
            
            multiplier2 =325/red_arrow.size[0]

            red_arrow = red_arrow.resize(width=multiplier2 * red_arrow.size[0])
            red_arrow = red_arrow.resize(height=multiplier2 * red_arrow.size[1])

            red_arrow  = red_arrow.set_position([150,1680-red_arrow.size[1]])

            rnd_sfx = AudioFileClip(f"SampleSfxs/{random.choice(os.listdir('SampleSfxs'))}")
            if rnd_sfx.duration > red_arrow_dur:
                rnd_sfx = rnd_sfx.subclip(0,red_arrow_dur)

            rnd_sfx = rnd_sfx.set_start(start_time)

            video_result.audio = CompositeAudioClip([video_result.audio,rnd_sfx])
        
            video_result = CompositeVideoClip([video_result,red_arrow])
        
        if add_rnd_sfx:
            video_result = add_rnd_sfxs(video_result)

        video_result = moviepy.audio.fx.all.volumex(video_result,all_vol)

        video_result.write_videofile(f"Videos/{name}{tries}.mp4",fps=fps,codec="libx264")
        
        #At the end of the creation process, you get asked if the result is good enough. If it isn't, the whole proccess will be reapeted
        #Answer yes or no
        answer = input("Are you satisfied? If not the video creation will start again all over: (Answer yes or no)")
        while not answer.lower() in ["yes","no"]:
            answer = input("Are you satisfied? ")
        
        if answer == "yes":
            print("Proccess done!")
            break
        elif answer == "no":
            print("Retrying...")
            continue
        


#The text object will follow a certain animation, in this instance its cords simulate the mathematical functions y = y0 - tan(2*t) and x = x0 + tan(t)
def text_random_movement(text_obj):

    #How long each frame of the animation will be
    time_per_part = 0.01
    #The multiplayer so the animation is clearer
    m = 20

    texts = []
    start_pos = [ 1080/2 - text_obj.size[0]/2 , 1920/4 - text_obj.size[1]/2 ]

    for time in range( int(text_obj.duration/time_per_part) ):
       
        sample_text = text_obj.set_position( [start_pos[0]+ -m*math.tan(2*time*time_per_part),start_pos[1]+m*math.tan(time*time_per_part)] ).set_start(time*time_per_part).set_duration(time_per_part)
        texts.append(sample_text)

    return texts




"!!! Variables needed to create video !!!"

#The folder from where the background footage is going to be generated, the folder should have more than 1 videos ( >= 2)
footage_folder = "Footage"

#The folder with the background music that will be used in the video
music_folder = "Music"

#The Font that is going to be used
font_used = "Font.ttf"

#The name of the video as an .mp4 file
video_name = "SampleVid"

#The path of the recoding of the AI recording
path_video = "video.mp4"



if __name__ == "__main__":
    create_video(footage_folder,music_folder,font_used,video_name,path_video) #There are a lot more parameters in the create_video func, they are explained in the func itself
