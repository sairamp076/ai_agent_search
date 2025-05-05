import re

def parse_steps(steps):
    reasoning_points, urls = [], []
    url_pattern = re.compile(r'https?://[^\s]+')
    for idx, (action, observation) in enumerate(steps, start=1):
        reasoning_points.append(f"Step {idx}: 🛠️ The agent used **{action.tool}** with input: '{action.tool_input}'.")
        if isinstance(observation, list) and all(isinstance(item, dict) for item in observation):
            for res_num, result in enumerate(observation, start=1):
                reasoning_points.append(
                    f"  Result {res_num}: 📄 **{result.get('title', 'No title')}**\n  🔗 {result.get('url', 'No URL')}\n  📝 {result.get('content', 'No content')[:200]}...")
                urls.append(result.get('url', ''))
        else:
            reasoning_points.append(f"Step {idx}: 👀 It observed: {observation}.")
            urls.extend(url_pattern.findall(str(observation)))
    return reasoning_points, urls
