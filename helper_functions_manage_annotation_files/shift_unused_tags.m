function newelements = shift_unused_tags(elements,tags_to_remove)
% This helper function gets a tweet format 'elements' array
% returns the array 'newelements' where tags that are not appearing
% are ignored, syllables with tags that appear in the 'tags_to_remove' vector
% are deleted and all remaining tags renumbered to be a continuous list.
newelements = elements;
for i = 1:numel(newelements)
    locs = find(ismember(newelements{i}.segType,tags_to_remove));
    newelements{i}.segAbsStartTimes(locs) = [];
    newelements{i}.segFileEndTimes(locs) = [];
    newelements{i}.segFileStartTimes(locs) = [];
    newelements{i}.segType(locs) = [];
end

syls = [];
for i = 1:numel(newelements)
    syls = unique(union(syls,newelements{i}.segType));
end

for i = 1:numel(newelements)
    for j = 1:numel(newelements{i}.segType)
        newelements{i}.segType(j) = find(syls == newelements{i}.segType(j));
    end
end

