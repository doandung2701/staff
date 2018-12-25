#standard main function flow chart 
Start;
init thing, seed_point, alpha, consider_matrix;
things.push(thing);
is_find_child = False;
while (True?){
	read_image(seed_point, 
	alpha);
	if (! is_find_child?) {
		if (things not empty?){
		  consider_thing = things.pop();
		  alpha = consider_thing.get_needed_alpha();
		  reset_history(consider_thing, consider_matrix);
			is_find_child = True;
		}
		else{
			break;
		}
	}
	else{
	  find_seed_ret, seed_point = find_seed(consider_thing, consider_matrix);
	  if (find_seed_ret==True?){
	    get_thing_ret, focus_thing = get_thing(consider_thing, seed_point);
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
