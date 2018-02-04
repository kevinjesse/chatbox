function [U S V] = randomsvd(A,uu,vv, m,n,k, INIT, maxit)

istrans = 0;
if numel(INIT) == 0
	Omega = randn(n, k);
else
	tt = min(k,size(INIT,2));
	Omega = INIT(:,1:tt);
	if tt < k
		Omega = [Omega randn(n,k-tt)];
	end
end
Y = A*Omega+uu*(vv'*Omega);
Atrans = A';
%Q = Y;
[Q R] = qr(Y,0);
for i=1:40
%for i=1:5
	if i>= maxit
		break;
	end
%	if m>n
		BB = Atrans*Q + vv*(uu'*Q);
		Y = A*BB + uu*(vv'*BB);
%		Y = A*(Atrans*Q)+VV*(uu'*Q);
%	else
%		Y = G*Q;
%	end
Qold = Q;
	[Q,R] = qr(Y,0);

	angle = min(svd(Q'*Qold));
%	fprintf('principle angle: %g\n', angle);
	if angle > 1-5e-2
%	if angle > 1-1e-8
		break
	end
end
[Q r] = qr(Y,0);
B = Q'*A+(Q'*uu)*vv';
[u S V] = svd(B,'econ');
U = Q*u;
