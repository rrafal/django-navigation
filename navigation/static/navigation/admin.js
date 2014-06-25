
var django = django || {}
django.navigation = django.navigation || {}


django.navigation.init_items_editor = function(options){
	var $ = jQuery;
	
	$(document).ready(function(){
		var $editor = $('#' + options.id);
		var $tree = $editor.find('.menuitem-tree > ul');
    	var $template = $editor.find('#menuitem-empty').detach();
    	var $max_prefix = $editor.find('[name="menuitem-max"]');
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
	            placeholder: 'ui-sortable-placeholder'
	        });
	  	}
        
        
    	
    	// initialize display
    	$.ajax({
			type: 'GET',
			url: location.pathname + "view/",
			success: function(data){
				// hiding the tree during editing to improve performance
				$tree.hide();
				$(data['items']).each(function(index, info){
					render_item(info);
				})
				$tree.show();
			}
    	});
		
		
		$editor.find('.add-item').each(function(){
			// autocomplete item title
			var $input = $(this).find('input');
			var $button = $(this).find('button');
			var autocomplete_url = $input.data('autocompleteUrl');

			$input.autocomplete({
				'source' : function(request, response){
					var query = {
						'term' : $input.val()
						};
					$.get( autocomplete_url, query, function(response_data){
						var data = [];

						$.each(response_data, function(index, item){
							var label = item.title + " ("+item.url+")";
							data.push({'label': label, 'value': item.url});
						});
						response(data);
					}, 'json'); 
				}
			});
			$input.bind("keypress", function(e) {
				if (e.keyCode == 13) {               
					e.preventDefault();
					$button.click();
				}
			});
		
    	
			// handle adding items
			$button.click(function(event){
				event.preventDefault()
				
				var url = $input.val();
				var info = {
					"status": "auto", 
					"parent_id": null, 
					"sitemap_item_title": null, 
					"title": "New Item", 
					"url": "/", 
					"sitemap_item_status": null, 
					"sitemap_item_id": null, 
					"id": null 
					};
					
				if(url == ''){
					add_item(info);
				} else {
					$.get( autocomplete_url, {'url': url}, function(data){
						if(data){
							info['sitemap_item_title'] = data[0]['title'];
							info['title'] = data[0]['title'];
							info['url'] = data[0]['url'];
							info['sitemap_item_status'] = data[0]['status'];
							info['sitemap_item_id'] = data[0]['id'];
						}
						add_item(info);
					}, 'json'); 
					$input.val('');
				}
			});
		});// end of add-item
    	
    	// handle deletion
    	$editor.on('click', '.delete-item', function(event){
    		event.preventDefault()
    		
    		var $item = $(this).closest('li').fadeOut(function(){
    			$(this).remove();
    		});
    	});
    	
		function add_item(info){
			var $item = render_item( info );
			$item.hide().fadeIn()
		}
    	function render_item(info){
    		var $list = null;
    		var $parent = null;
    		
    		if(info['parent_id']){
				$parent = $tree.find('li.menuitem-' + info['parent_id']);
				$list = $parent.children('ul');
			} else {
				$list = $tree
			}
			var html = $template.html();
			var index = parseInt($max_prefix.val()) + 1;
			$max_prefix.val(index);
			info['prefix'] = index;
			if( ! info['id'] ){
				info['id'] = 'new-'+index;
			}

			jQuery.each(info, function(key, value){
				html = html.replace( new RegExp('__'+key+'__', 'g'), value === null ? '' : value );
			});
			
			// update UI
			var $item = $('<li class="menuitem-tree-item"></li>').html(html);
			$item.addClass('menuitem-' + info['id']);
			$item.find('.menuitem-status-input').val( info['status'] );
			
			if( info.sitemap_item_id ){
				$item.find('.menuitem-url-input').prop('readonly', true);
			} else {
				$item.find('.menuitem-sitemap-item-row').hide();
			}
			if( has_sitemap){
  				$item.find('.delete-item').hide();
  			}

  			// append
  			$item.appendTo($list.get(0));
  			return $item;
    	}
    	
    	// update ordering
    	$editor.closest('form').submit(function(){
    		$editor.find('.menuitem-parent-id-input').val('');
    		$editor.find('.menuitem-tree-item').each(function(){
    			var id = $(this).children('.menuitem-content').find('.menuitem-id-input').val();
    			$(this).children('ul').find('.menuitem-parent-id-input').val(id);
    		});
    		$editor.find('.menuitem-order-input').each(function(index){
    			$(this).val(index);
    		});
    	});
    	
	});
};
