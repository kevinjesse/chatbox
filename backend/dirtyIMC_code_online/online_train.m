function [W, H] = online_train(Xg, Xm, Xa, Y_path, R, W_path, H_path)
load(Y_path);
load(W_path);
load(H_path);

gm = Xg(1,:)'*Xm(1,:);
ga = Xg(1,:)'*Xa(1,:);
ma = Xm(1,:)'*Xa(1,:);
gm = gm(:);
ga = ga(:);
ma = ma(:);
X(1,:) = [gm' ga' ma'];
X(isnan(X)) = 0; X(isinf(X)) = 0;



l1=.1;
l2=.1; 
lr = .00001;



precision = .0000001;
%precision = .0000001;
iters = 11;
% iters = 500;
cost_history = zeros(iters,1);





% for i = 1:iters
i = 1;
prev_cost = 1/precision;
cost = Inf;
while abs(prev_cost - cost) > precision && (i < iters)
    prev_cost = cost;
%     
%      Wv = online_update_weightsW(X, Y(ind,:), R(ind), W(ind,:), H(ind,:), l1, lr);
%      Hv = online_update_weightsH(X, Y(ind,:), R(ind), W(ind,:), H(ind,:), l2, lr);

     Wt = online_update_weightsW(X, Y, R, W, H, l1, lr);
     Ht = online_update_weightsH(X, Y, R, W, H, l2, lr);    
    
%     Wt = W;
%     Ht = H;
%     Wt(ind,:) = Wv;
%     Ht(ind,:) = Hv;
    cost = costFunction(X, Y, R, Wt, Ht, l1, l2);
    cost_history(i) = cost;
%     if mod(i,10) == 0
    fprintf("iter: %d | cost: %d\n", i, cost);
    %end
    if cost > prev_cost
        disp("here")
        break
    end
    W= Wt;
    H= Ht;
    i= i+ 1;    
    
end

%[J, grad1, grad2] = costFunction(X, Y, R, theta1, theta2, lambda1, lambda2);

%function [J, grad1, grad2] = costFunction(X, Y, R, t1, t2, lambda1, lambda2)


