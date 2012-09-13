
var django = django || {}
django.navigation = django.navigation || {}


django.navigation.init_items_editor = function(options){
	var $ = jQuery;
	
	$(document).ready(function(){
		var $editor = $('#' + options.id);
		var $tree = $editor.find('.menuitem_set_editor_tree > ul');
		
		var template = $( "#" + options.template_id ).template();
    	
    	var csrf_name = 'csrfmiddlewaretoken';
    	var csrf_value = $editor.closest('form').find('input[name='+csrf_name+']').val();
    	
    	var has_sitemap = $editor.closest('form').find('#id_sitemap').val() != '';
		
		
		if( has_sitemap) {
			$editor.find('.add-item').hide();
		}else {	
			// allow sorting	
			$tree.nestedSortable({
	            handle: 'div',
	            listType: 'ul',
	            items: 'li',
	            toleranceElement: '> div',
	            placeholder: 'ui-sortable-placeholder',
	            stop: function(event, ui){
	            	update_item_position(ui.item);
	            }
	        });
	  	}
        
    	
    	
    	
    	// initialize display
    	$.ajax({
			type: 'GET',
			url: location.pathname + "view/",
			success: function(data){
				$(data['items']).each(function(index, info){
					// show item
					render_item(info);
				})
				
				
			}
    	});
    	
    	// auto save changes
    	$editor.on('change', ':input', function(){
    		var $item = $(this).closest('li');
    		update_item_info($item);
    	});
    	
    	// handle adding items
    	$editor.find('.add-item a').click(function(event){
    		event.preventDefault()
    		
    		// create item on server
    		var data = {};
    		data[csrf_name] = csrf_value;
    		
    		$.ajax({
    			type: 'POST',
    			url: location.pathname + "add_item/",
    			data: data,
    			success: function(data){
					var $item = render_item(data.item);
	  				$item.hide().fadeIn()
    			}
    		});
    		
    	});
    	
    	// handle deletion
    	$editor.on('click', '.delete-item', function(event){
    		event.preventDefault()
    		
    		var $item = $(this).closest('li');
    		
    		delete_item($item);
    	});
    	
    	function render_item(info){
    		var $list = null;
    		var $parent = null;
    		
    		if(info['parent_id']){
				$parent = $tree.find('li.menuitem-' + info['parent_id']);
				$list = $parent.children('ul');
			} else {
				$list = $tree
			}
			var $item = $.tmpl( template, info ).appendTo( $list );
			var $content = $item.children('.menuitem-content');
			$content.find('.menuitem-status-input').val( info['status'] );
			
			console.log($content.find('.menuitem-sitemap-item-row'));
			if( info.sitemap_item_id ){
				$content.find('.menuitem-url-input').prop('readonly', true);
				$content.find('.menuitem-sitemap-item-row').show();
			} else {
				$content.find('.menuitem-url-input').prop('readonly', false);
				$content.find('.menuitem-sitemap-item-row').hide();
			}
			if( has_sitemap){
  				$content.find('.delete-item').hide();
  			}
  			return $item;
    	}
    	
    	// update item
    	function update_item_position(item){
    		var $item = $(item);
        	var $parent = $item.parent().parent('li');
        	var parent_id = $parent.attr('data-id');
        	
        	var $parent_input = $item.children('.menuitem-content').find('.menuitem-parent-input');
        	if($parent_input.val() == parent_id){
        		return;
        	}
        	
    		$parent_input.val(parent_id);
    		
    		var data = {};
    		data[csrf_name] = csrf_value;
    		data['id'] = $item.attr('data-id');
    		data['parent'] = parent_id ? parent_id : '';
    		
    		$.ajax({
    			type: 'POST',
    			url: location.pathname + "update_item/",
    			data: data,
    		});
    	}
    	
    	function update_item_info(item){
    		var $item = $(item);
  			var $content = $item.children('.menuitem-content');
        	
    		var data = {};
    		data[csrf_name] = csrf_value;
    		data['id'] = $item.attr('data-id');
    		data['title'] = $content.find('.menuitem-title-input').val();
    		data['url'] = $content.find('.menuitem-url-input').val();
    		data['status'] = $content.find('.menuitem-status-input').val();
    		
    		$.ajax({
    			type: 'POST',
    			url: location.pathname + "update_item/",
    			data: data,
    		});
    	}
    	
    	function delete_item(item){
    		var $item = $(item);
    		
    		// delete item on server
    		var data = {};
    		data[csrf_name] = csrf_value;
    		data['id'] = $item.attr('data-id');
    		
    		$.ajax({
    			type: 'POST',
    			url: location.pathname + "delete_item/",
    			data: data,
    		});
    		
    		// hide it
    		$item.fadeOut();
    	}
		
	});
};
