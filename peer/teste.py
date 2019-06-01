def fat_per(x):
	a = 100/x
	l = []
	for i in range(x):
		l.append(a)
	for y in range(len(l)-1):
		l[y] = l[y]/2
		l[y+1] += l[y]
		return l


def pages(num_pages, peers):
	aux_peers = peers
	peers = len(peers)

	if peers == 1:
		return[[aux_peers[0], [i for i in range(1, num_pages+1)]]]

	percents = fat_per(peers)
	percents.sort(reverse=True)

	w_peers = []

	for p in percents:
		a = (p/100) * num_pages
		w_peers.append(round(a))

	if sum(w_peers) > num_pages:
		w_peers[0] = w_peers[0] - (sum(w_peers) - num_pages)
	if sum(w_peers) < num_pages:
		w_peers[0] = w_peers[0] + (num_pages-sum(w_peers))

	pages_by_hosts = []

	for ip in range(peers):
		if ip == 0:
			pages_by_hosts.append([aux_peers[ip], [i for i in range(1, w_peers[ip] + 1)]])
		else:
			pages_by_hosts.append([aux_peers[ip], [i for i in range(pages_by_hosts[-1][1][-1]+1, pages_by_hosts[-1][1][-1] + w_peers[ip] + 1)]])

	return pages_by_hosts


p = pages(15, ['a', 'b', 'c'])
print(p)