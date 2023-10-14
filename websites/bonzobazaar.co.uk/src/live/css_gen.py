import random
'''
      @keyframes load1 {
           0% {clip-path: polygon(0% 0%, 100% 0%, 100% 10%, 0% 10%);}
           50% {clip-path: polygon(0% 0%, 100% 0%,  100% 50%, 0% 50%);}
           100%{
                width: 400px;height: 400px;
                object-fit: cover;
                }
      }
'''


class keyframe(object):
   skeleton = '''
   @keyframes load{id_no} '''
   end = '''        100% {
                width: 400px;height: 400px;
                object-fit: cover;
      }
   }

   '''
   def __init__(self, no_images, no_frames):
      self.no_images = no_images
      self.no_frames = no_frames
      self.image_factory()


   def frame_factory(self, image):
      frames = ''
      block_size = 100 / self.no_frames
      begin = self.skeleton.format(id_no = image)
      for frame in range(self.no_frames):
         percent_complete = random.randint(frame * block_size, (frame + 1) * block_size)
         frames += f'''
        {percent_complete}%''' + "{" + f"clip-path: polygon(0% 0%, 100% 0%, 100% {percent_complete}%, 0% {percent_complete}%)" + '''}
'''
        
      return begin + "{" + frames + self.end

   def image_factory(self):
      self.images = {}
      for image in range(self.no_images):
         self.images[image] = self.frame_factory(image)
          
   
   

if __name__ == "__main__":
   my_frames = keyframe(5, 10)
   for im in my_frames.images:
      print(my_frames.images[im])
