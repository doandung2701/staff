Main function;
is_find_child = False;
while (True?){
	imread();
	if (! is_find_child?) {
		if (things not empty?){
		  consider_thing = things.pop();
		  alpha = get_needed_alpha();
		  reset_history(consider_thing);
			is_find_child = True;
		}
		else{
			break;
		}
	}
	else{
	  find_seed_ret, seed_point = find_seed(consider_matrix);
	  if (find_seed_ret==True?){
	    get_thing_ret, focus_thing = get_thing();
	    if (get_thing_ret==True?){
				add_thing(focus_thing);
	    }
	    mark_consider(focus_thing);
	  }
	  else{
	    is_find_child = False;
	  }
	}
}
end;


#####
Main function;
is_find_child = False;
while (True?){
	model.eye.imread();
	if (! is_find_child?) {
		if (model.brain.things not empty?){
		  model.brain.consider_thing = model.brain.things.pop();
		  model.brain.eye_status.alpha = model.brain.consider_thing.get_needed_alpha();
		  model.brain.reset_history(model.brain.consider_thing);
			is_find_child = True;
		}
		else{
			break;
		}
	}
	else{
	  find_seed_ret, model.brain.eye_status.seed_point = model.brain.consider_thing.find_seed(model.brain.consciousness.consider_matrix);
	  if (find_seed_ret==True?){
	    get_thing_ret, model.brain.focus_thing = model.get_thing();
	    if (get_thing_ret==True?){
				model.brain.add_thing(model.brain.focus_thing, relation='child');
	    }
	    model.brain.mark_consider(model.brain.focus_thing);
	  }
	  else{
	    is_find_child = False;
	  }
	}
}
end;

#####
Main function;
is_find_child = False;
while (True?){
	imread();
	if (! is_find_child?) {
		if (things not empty?){
	        consider_thing = things.pop();
		    alpha = get_needed_alpha();
            reset_history(consider_thing);
		    is_find_child = True;
		}
		else{
			break;
		}
	}
	else{
	    find_seed_ret, seed_point = find_seed(consider_matrix);
	    if (find_seed_ret==True?){
	        get_thing_ret, focus_thing = get_thing();
	        if (get_thing_ret==True?){
				add_thing(focus_thing);
	        }
	        mark_consider(focus_thing);
	    }
	    else{
	        is_find_child = False;
	    }
	}
}

#####
model = App('')
is_find_child = False;
while (True?){
	model.eye.imread();
	if (! is_find_child?) {
		if (model.brain.things not empty?){
	        model.brain.consider_thing = model.brain.things.pop();
		    model.brain.eye_status.alpha = model.brain.consider_thing
		        .get_needed_alpha();
            model.brain.reset_history(model.brain.consider_thing);
		    is_find_child = True;
		}
		else{
			break;
		}
	}
	else{
	    find_seed_ret, model.brain.eye_status.seed_point = model.brain.
	        consider_thing.find_seed(model.brain.consciousness.consider_matrix);
	    if (find_seed_ret==True?){
	        get_thing_ret, model.brain.focus_thing = model.get_thing();
	        if (get_thing_ret==True?){
				model.brain.add_thing(model.brain.focus_thing, relation='child');
	        }
	        model.brain.mark_consider(model.brain.focus_thing);
	    }
	    else{
	        is_find_child = False;
	    }
	}
}

#####



def get_thing(self):
		potential_window, mask = sl.grow_region(self.brain.consciousness.picture.copy(), self.eye.eye_status.seed_point, threshold=self.eye.eye_quality)
		potential_thing = Thing(potential_window, mask=mask, picture=self.brain.consciousness.picture)
		if not Thing.check_satify_condition(potential_thing):
			return False, potential_thing
		is_exist = self.update_new_thing(potential_thing)
		if not is_exist:
			return True, potential_thing
		return False, potential_thing
 
