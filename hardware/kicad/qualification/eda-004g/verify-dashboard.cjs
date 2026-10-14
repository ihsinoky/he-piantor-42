// Submission-only Node VM DOM check; no browser or EDA experiment claimed.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const repo = path.resolve(__dirname, '../../../..');
const data = fs.readFileSync(path.join(repo, 'task/data/project-status.js'), 'utf8');
const renderer = fs.readFileSync(path.join(repo, 'task/dashboard.js'), 'utf8');

function render(substitute) {
  const elements = new Map();
  const document = { getElementById(id) {
    if (!elements.has(id)) elements.set(id, {
      value: '', textContent: '', innerHTML: '', href: '', className: '',
      addEventListener() {}, insertAdjacentHTML(_position, html) { this.innerHTML += html; }
    });
    return elements.get(id);
  }};
  const context = {window: {}, document};
  vm.createContext(context);
  vm.runInContext(data, context);
  const p = context.window.PROJECT_STATUS;
  if (substitute) substitute(p);
  vm.runInContext(renderer, context);
  return {p, elements};
}

const normal = render();
assert.equal(normal.p.latestEvaluation.id, 'EDA-004G');
assert.equal(normal.elements.get('issue-link').textContent, 'Issue #85');
assert.equal(normal.elements.get('report-link').href, '../docs/native-main-routing-qualification.md');
assert.ok(normal.elements.get('history-list').innerHTML.includes('merged PR #84（受入済み）'));
assert.ok(normal.elements.get('technical-status').textContent.includes('ERC_UNQUALIFIED'));
assert.ok(normal.elements.get('qualification-map').innerHTML.includes('未実施'));

const swapped = render(p => {
  p.latestEvaluation.id = 'EDA-TEST';
  p.latestEvaluation.title = 'temporary evaluation title';
  p.latestEvaluation.workStatus = 'temporary work state';
  p.latestEvaluation.technicalStatus = 'temporary technical state';
  p.latestEvaluation.issue = {id:'TEST', url:'https://example.invalid/issue'};
  p.latestEvaluation.acceptedRecord = {id:'TEST', url:'https://example.invalid/pr', status:'temporary record'};
  p.source.reportUrl = '../docs/temporary-test-report.md';
  p.latestEvaluation.coverage = p.latestEvaluation.coverage.map(c => ({...c, result:'未実施', detail:'temporary coverage'}));
});
assert.equal(swapped.elements.get('evaluation-id').textContent, '評価 EDA-TEST');
assert.equal(swapped.elements.get('evaluation-title').textContent, 'temporary evaluation title');
assert.equal(swapped.elements.get('technical-status').textContent, 'temporary technical state');
assert.equal(swapped.elements.get('work-status').textContent, 'temporary work state');
assert.equal(swapped.elements.get('issue-link').href, 'https://example.invalid/issue');
assert.equal(swapped.elements.get('pr-link').href, 'https://example.invalid/pr');
assert.equal(swapped.elements.get('report-link').href, '../docs/temporary-test-report.md');
assert.ok(swapped.elements.get('qualification-map').innerHTML.includes('EDA-TEST'));
assert.ok(!swapped.elements.get('qualification-map').innerHTML.includes('EDA-004G'));
console.log(JSON.stringify({javascript_syntax_and_dom_render:true, latest_record_substitution:true, historical_pr84_accepted:true, browser_visual_test:false}));
