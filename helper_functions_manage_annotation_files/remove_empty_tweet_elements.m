function [newkeys, newelements] = remove_empty_tweet_elements(path_to_annotation_file);
% This helper function gets a path to a tweet format annotation file and
% returns the arrays 'keys' and 'elements' after removing empty elements.

params = load(path_to_annotation_file);

locs = find(cellfun(@(x)~isempty(x.segType), params.elements));

newkeys = params.keys(locs);
newelements = params.elements(locs);
