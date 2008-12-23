import sublime, sublimeplugin

class SearchCommand(sublimeplugin.TextCommand):
   def run(self, view, args):
      failesafe = 1000
      counter = 0
      result = []
      files_i_have_been = []
      view_list = view.window().views()
      pattern = sublime.getClipboard()
      
      for a_view in view_list:
         # avoid re-searching same view (if opened twice)
         if a_view.fileName() in files_i_have_been:
            continue
         else:  
            files_i_have_been.append(a_view.fileName())
         
         # search   
         next_region = view.line(0) # start from 0
         while next_region is not False:
            region = a_view.find(pattern, next_region.begin(), 0)
            if region is not None:
               (row, col) = a_view.rowcol(region.begin())
               s = a_view.substr(a_view.line(region))
               full_s = a_view.fileName() + ":" + str(row) + ": " + s
               result.append(full_s)
               next_region = self.advance_line(view, region)
            else:
               break
            
            counter += 1
            if counter > failesafe:
               break
            
      view.window().showQuickPanel("", "", result)  
      #for line in result:
      #   print line
      
   def isEnabled(self, view, args):
      if view.fileName() is not None:
         return True
      else:
         return False
   
   def advance_line(self, view, last_region):
      (row, col) = view.rowcol(last_region.begin())
      next_point = view.textPoint(row+1, 0)
      next_region = view.line(next_point)
      
      if next_region.begin() > last_region.end():
         return next_region
      else:
         return False