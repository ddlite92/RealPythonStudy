info_viewlayers_compositing = {"English": """<p><b>Handling Compositing (when present)</b></p>
<p>The scene’s compositing node tree combines the rendered view layers via <i>Render Layer</i> nodes. When rendering view layers independently with B-renderon, the node tree may not always function as expected, since only the <i>Render Layer</i> node for the view layer being rendered will actually produce any output.</p>

<p>B-renderon provides different options for how to handle this:</p>

<p><b>1) Auto (default):</b> Automatically disable compositing if multiple <i>Render Layer</i> nodes are present. If there is exactly one, only use compositing when rendering the view layer assigned to that render layer node.</p>

<p><b>2) Replicate:</b> If only one <i>Render Layer</i> node is present, it reassigns it to match the view layer currently being rendered, ensuring the same compositing setup is applied across view layers. Similar to Auto, this option disables compositing if multiple <i>Render Layer</i> nodes exist.</p>

<p><b>3) Disable:</b> Just disable compositing altogether.</p>

<p><b>4) Leave as is:</b> Leaves the compositing setup unchanged, rendering the view layer with the existing node tree configuration. This option is generally not recommended, as it may produce unexpected results.</p>

<p><b>Note:</b> If the scene doesn't use compositing, all of these options will have no effect, and the render will proceed as normal.</p>
"""

, "Castellano": """
<p><b>Manejo de Composición (si la hay)</b></p>
<p>El árbol de nodos de composición de la escena combina view layers a través de nodos <i>Render layer</i>. Al renderizar distintos view layers de manera independiente con B-renderon, el árbol de nodos puede no funcionar como se espera, ya que solo el nodo <i>Render layer</i> para la view layer que se está renderizando producirá algún resultado.</p>

<p>B-renderon proporciona diferentes opciones para manejar esto:</p>

<p><b>1) Automático (predeterminado):</b> Deshabilitar automáticamente la composición si hay múltiples nodos <i>Render layer</i> presentes. Si hay exactamente uno, solo utilizar composición al renderizar la view layer asignada a ese nodo.</p>

<p><b>2) Replicar:</b> Si solo hay un nodo de <i>Render layer</i> presente, lo reasigna para que coincida con la view layer que se está renderizando actualmente, asegurando que se aplique la misma configuración de composición en todas las view layers. Similar a Automático, esta opción desactiva la composición si existen múltiples nodos de <i>Render layer</i>.</p>

<p><b>3) Deshabilitar:</b> Simplemente desactiva la composición por completo.</p>

<p><b>4) Dejar como está:</b> Deja la configuración de composición sin cambios, renderizando la view layer con la configuración actual del árbol de nodos. Esta opción generalmente no se recomienda, ya que puede producir resultados inesperados.</p>

<p><b>Nota:</b> Si la escena no usa composición, ninguna de estas opciones tendrá efecto y el renderizado continuará con normalidad.</p>

""",
"中文": """
<p><b>处理合成（当存在时）</b></p>
<p>场景的合成节点树通过 <i>Render Layer</i> 节点组合已渲染的视图层。在使用 B-renderon 独立渲染视图层时，节点树可能无法按预期运行，因为只有正在渲染的 <i>view layer</i> 的 <i>Render Layer</i> 节点会产生输出。</p>

<p>B-renderon 提供了不同的选项来处理这种情况：</p>

<p><b>1) 自动（默认）:</b> 如果存在多个 <i>Render Layer</i> 节点，则自动禁用合成。如果只有一个节点，则只在渲染分配给该 <i>Render Layer</i> 节点的 <i>view layer</i> 时使用合成。</p>

<p><b>2) 复制:</b> 如果只存在一个 <i>Render Layer</i> 节点，它将重新分配以匹配当前正在渲染的 <i>view layer</i>，确保在所有视图层中应用相同的合成设置。类似于自动选项，该选项会在存在多个 <i>Render Layer</i> 节点时禁用合成。</p>

<p><b>3) 禁用:</b> 完全禁用合成。</p>

<p><b>4) 保持原样:</b> 保持合成设置不变，使用现有的节点树配置渲染视图层。此选项通常不建议使用，因为可能会产生意外结果。</p>

<p><b>注意:</b> 如果场景没有使用合成，这些选项将无效，渲染将照常进行。</p>


"""
}

info_tokens_collections = {
    "English": """
<p><strong>Assigning output filepath tokens to collections</strong></p>
<p>By clicking/shift+clicking on the token buttons, you can assign token keys to different collections. Then, in the output filepath window, you can use the tokens to incorporate the desired collection names in the output filepath.</p>
<p>Collection tokens have the form [COLLECTION][<em>key</em>] where <em>key</em> is a letter from A to E for manually set token keys. For example, the first time you click a token button an A will appear. If you then introduce [COLLECTION][A] to the output pattern in the output filepath window, it will get replaced by the corresponding collection name for all selected jobs</p>
""",
"Castellano": """
<p><strong>Asignación de tokens de ruta de salida a colecciones</strong></p>
<p>Al hacer click/shift+click en los botones de tokens, se asignan claves de token a diferentes colecciones. Luego, en la ventana de ruta de salida, se puede usar los tokens para incorporar los nombres de colecciones deseados en la ruta/nombre de salida.</p>
<p>Los tokens de colección tienen la forma [COLECCIÓN][<em>clave</em>] donde <em>clave</em> es una letra de la A a la E para las claves de token establecidas manualmente. Por ejemplo, al hacer click por primera vez en un botón de token, aparecerá una A. Luego, al introducir [COLECCIÓN][A] en el patrón de salida en la ventana de ruta de salida, se reemplazará por el nombre de la colección correspondiente.</p>
""",
"中文": """
<p><strong>将输出文件路径令牌分配给集合</strong></p>
<p>通过单击/按住Shift并单击令牌按钮，您可以将令牌键分配给不同的集合。然后，在输出文件路径窗口中，您可以使用这些令牌将所需的集合名称纳入输出文件路径中。</p>
<p>集合令牌的形式为 [COLLECTION][<em>key</em>]，其中 <em>key</em> 是从 A 到 E 的字母，表示手动设置的令牌键。例如，当您第一次单击令牌按钮时，将出现 A。如果您随后在输出文件路径窗口的输出模式中引入 [COLLECTION][A]，它将被所有选定作业的相应集合名称替换。</p>
"""
}

info_split_collections = {
    "English": """<p><strong>Splitting Selected Collections</strong></p>
<p>With two or more same-level collections selected, this operator splits the job into multiple jobs&mdash;one for each selected collection. For each job, one collection will be enabled while the others will be disabled. The enabled collection will be assigned a token key, starting with <strong>S</strong> the first time the operator is run.</p>
<p>For more details on collection tokens, refer to the <em>Token Info</em> popup.</p>""",
    "Castellano": """
<p><strong>Repartir colecciones seleccionadas</strong></p>
<p>Con dos o más colecciones del mismo nivel seleccionadas, este operador divide el trabajo en múltiples trabajos: uno para cada colección seleccionada. Para cada trabajo, se habilitará una colección mientras que las demás estarán deshabilitadas. A la colección habilitada se le asignará una clave de token, comenzando con <strong>S</strong> la primera vez que se ejecute el operador.</p>
<p>Para más detalles sobre los tokens de colección, consulta la ventana emergente de <em>Información de tokens</em>.</p>
""",
    "中文": """
<p><strong>拆分选定的集合</strong></p>
<p>当选择了两个或更多同级集合时，此操作符会将工作拆分为多个工作—每个选定的集合对应一个工作。对于每个工作，一个集合将被启用，而其他集合将被禁用。启用的集合将被分配一个令牌键，第一次运行操作符时，令牌键将从<strong>S</strong>开始。</p>
<p>有关集合令牌的更多详细信息，请参阅<em>令牌信息</em>弹窗。</p>
"""

}
