max = 0;
for i = 1:340
    t = sum(Obs(i,:)==5) + sum(Obs(i,:)==4);
    if t>max
        max = t;
    end
end
disp(max)
